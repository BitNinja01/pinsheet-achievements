"""Post-round acknowledgment screen — ported from PinSheet core."""
import asyncio
import logging
import random
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Static
from textual.containers import Horizontal, Vertical
from data import get_all_rounds, get_courses, get_handicap_benchmarks, load_settings
from handicap import calc_handicap_index
from windows import WindowedRounds
from stats_scoring import calc_personal_bests
from screens.animations import SpinReveal
from screens.season_patterns import PATTERNS, PatternWidget

_log = logging.getLogger("achievements")


def _figlet(value: str) -> str:
    return "\n".join(SpinReveal.render_lines(value))


def _gir_count(holes: dict) -> int:
    return sum(1 for h in holes.values() if h.get("gir") == "H")


def _fir_count(holes: dict) -> int:
    return sum(1 for h in holes.values() if h.get("fairway") == "H")


def _putt_total(holes: dict) -> int:
    return sum(int(h["putts"]) for h in holes.values() if h.get("putts"))


def _birdie_count(holes: dict, courses: dict, course_name: str) -> int:
    course_holes = courses.get(course_name, {}).get("holes", {})
    count = 0
    for hole_num, h in holes.items():
        par = int(course_holes.get(str(hole_num), {}).get("par", 0))
        if par and h.get("gross") and int(h["gross"]) < par:
            count += 1
    return count


class RoundAcknowledgmentScreen(Screen):

    LAYERS = ("background", "default")

    BINDINGS = [
        Binding("space", "continue_", "Continue"),
        Binding("enter", "continue_", "Continue", show=False),
    ]

    def __init__(self, round_data: dict, has_details: bool = True) -> None:
        super().__init__()
        self._round = round_data
        self._has_details = has_details
        self._pattern = random.choice(PATTERNS)()
        self._figlet_texts: list[str] = []
        self._block_is_record: list[bool] = []

    def compose(self) -> ComposeResult:
        highlights = self._build_highlights()
        if not highlights:
            yield PatternWidget(None, id="ack-pattern")
            yield Static("Saved. 18 holes in the books.", id="ack-fallback")
            yield Footer()
            return

        raw_figlets = [_figlet(str(b["value"])) for b in highlights]
        max_w = max(max(len(line) for line in ft.split("\n")) for ft in raw_figlets)
        self._figlet_texts = [
            "\n".join(line.center(max_w) for line in ft.split("\n"))
            for ft in raw_figlets
        ]
        self._block_is_record = [b.get("is_record", False) for b in highlights]

        accent = self.app.current_theme.primary
        pattern_widget = PatternWidget(self._pattern, id="ack-pattern")
        pattern_widget.styles.color = accent
        yield pattern_widget
        with Horizontal(classes="ack-content"):
            for i, block in enumerate(highlights):
                is_record = block.get("is_record", False)
                block_color = "#FFD700" if is_record else accent
                figlet_static = Static(self._figlet_texts[i], classes="ack-figlet")
                figlet_static.styles.opacity = 0.0
                figlet_static.styles.color = block_color
                figlet_static.styles.border = ("round", block_color)
                label_static = Static(block["label"], classes="ack-label")
                label_static.styles.opacity = 0.0
                label_static.styles.color = block_color
                ctx_widgets = []
                for line_key in ("l20_line", "bench_line"):
                    raw = block.get(line_key)
                    if not raw:
                        continue
                    parts = raw.split(" ", 1)
                    num_color = "#FFD700" if is_record else accent
                    markup = f"[{num_color}]{parts[0]}[/] {parts[1]}" if len(parts) == 2 else raw
                    w = Static(markup, classes="ack-context")
                    w.styles.opacity = 0.0
                    ctx_widgets.append(w)
                with Vertical(classes="ack-stat-block") as vblock:
                    if is_record:
                        vblock.styles.border = ("round", "#FFD700")
                    yield figlet_static
                    yield label_static
                    for w in ctx_widgets:
                        yield w
        yield Footer()

    def on_mount(self) -> None:
        _log.info("screen: round acknowledgment")
        if self._figlet_texts:
            self._animate_blocks()

    @work(exclusive=True)
    async def _animate_blocks(self) -> None:
        _shimmer_colors = ["#B8860B", "#DAA520", "#FFD700", "#FFEC8B", "#FFD700", "#DAA520"]
        await asyncio.sleep(0.5)
        figlet_widgets = list(self.query(".ack-figlet"))
        for idx, figlet_widget in enumerate(figlet_widgets):
            text = self._figlet_texts[idx]
            lines = text.split("\n")
            width = SpinReveal.calc_width(lines)
            total_frames = SpinReveal.TOTAL_FRAMES
            for frame in range(total_frames + 1):
                figlet_widget.styles.opacity = min(1.0, frame / 8)
                figlet_widget.update(SpinReveal.build_frame(lines, width, frame, total_frames))
                await asyncio.sleep(SpinReveal.FRAME_DELAY)
            is_record = self._block_is_record[idx] if idx < len(self._block_is_record) else False
            if is_record:
                for _ in range(4):
                    for color in _shimmer_colors:
                        figlet_widget.styles.color = color
                        await asyncio.sleep(0.07)
                figlet_widget.styles.color = "#FFD700"
            block = figlet_widget.parent
            for child in block.children:
                if child is figlet_widget:
                    continue
                for step in range(9):
                    child.styles.opacity = step / 8
                    await asyncio.sleep(0.033)
                child.styles.opacity = 1.0

    def _build_highlights(self) -> list[dict]:
        round_data = self._round
        has_details = self._has_details

        all_rounds = get_all_rounds(limit=21)
        all_rounds_full = get_all_rounds()
        settings = load_settings()
        w = WindowedRounds(all_rounds, get_courses(), None, settings.get("include_9hole", True))
        hi = calc_handicap_index(w.last_20, w.use_9hole)

        round_date = round_data.get("date", "")
        round_index = str(round_data.get("index", ""))
        l20 = [
            r for r in all_rounds
            if not (r.get("date") == round_date and str(r.get("index", "")) == round_index)
        ][:20]

        benchmarks = get_handicap_benchmarks(int(hi)) if hi is not None else None

        stats_pool = []

        # differential
        try:
            this_diff = float(round_data["differential"])
        except (KeyError, ValueError, TypeError):
            this_diff = None

        if this_diff is not None:
            l20_diffs = [float(r["differential"]) for r in l20 if r.get("differential") not in (None, "")]
            l20_diff_avg = sum(l20_diffs) / len(l20_diffs) if l20_diffs else None
            bench_diff = hi
            stats_pool.append({
                "key": "diff",
                "this": this_diff,
                "l20_avg": l20_diff_avg,
                "bench": bench_diff,
                "higher_better": False,
                "label": "Differential",
                "fmt": lambda v: f"{float(v):.1f}",
            })

        if has_details:
            holes = round_data.get("holes", {})
            courses = get_courses()
            course_name = round_data.get("course", "")

            this_gir = _gir_count(holes)
            l20_gir_avgs = []
            for r in l20:
                if r.get("holes"):
                    l20_gir_avgs.append(_gir_count(r["holes"]))
            l20_gir_avg = sum(l20_gir_avgs) / len(l20_gir_avgs) if l20_gir_avgs else None
            bench_gir_pct = benchmarks.get("gir_pct") if benchmarks else None
            bench_gir = (bench_gir_pct * 18 / 100) if bench_gir_pct is not None else None
            stats_pool.append({
                "key": "gir",
                "this": this_gir,
                "l20_avg": l20_gir_avg,
                "bench": bench_gir,
                "higher_better": True,
                "label": "Greens in Regulation",
                "fmt": lambda v: str(int(round(v))),
            })

            this_fir = _fir_count(holes)
            l20_fir_avgs = []
            for r in l20:
                if r.get("holes"):
                    l20_fir_avgs.append(_fir_count(r["holes"]))
            l20_fir_avg = sum(l20_fir_avgs) / len(l20_fir_avgs) if l20_fir_avgs else None
            bench_fir_pct = benchmarks.get("fir_pct") if benchmarks else None
            bench_fir = (bench_fir_pct * 18 / 100) if bench_fir_pct is not None else None
            stats_pool.append({
                "key": "fir",
                "this": this_fir,
                "l20_avg": l20_fir_avg,
                "bench": bench_fir,
                "higher_better": True,
                "label": "Fairways Hit",
                "fmt": lambda v: str(int(round(v))),
            })

            this_putts = _putt_total(holes)
            l20_putt_avgs = []
            for r in l20:
                if r.get("holes"):
                    l20_putt_avgs.append(_putt_total(r["holes"]))
            l20_putts_avg = sum(l20_putt_avgs) / len(l20_putt_avgs) if l20_putt_avgs else None
            bench_putts = benchmarks.get("putts") if benchmarks else None
            stats_pool.append({
                "key": "putts",
                "this": this_putts,
                "l20_avg": l20_putts_avg,
                "bench": bench_putts,
                "higher_better": False,
                "label": "Total Putts",
                "fmt": lambda v: str(int(round(v))),
            })

            this_birdies = _birdie_count(holes, courses, course_name)
            l20_birdie_avgs = []
            for r in l20:
                if r.get("holes") and r.get("course"):
                    l20_birdie_avgs.append(_birdie_count(r["holes"], courses, r["course"]))
            l20_birdies_avg = sum(l20_birdie_avgs) / len(l20_birdie_avgs) if l20_birdie_avgs else None
            stats_pool.append({
                "key": "birdies",
                "this": this_birdies,
                "l20_avg": l20_birdies_avg,
                "bench": None,
                "higher_better": True,
                "label": "Birdies",
                "fmt": lambda v: str(int(round(v))),
            })

        max_blocks = 1 if not has_details else 3
        selected = []

        all_prior = [
            r for r in all_rounds_full
            if not (r.get("date") == round_date and str(r.get("index", "")) == round_index)
        ]

        def _ctx_lines(stat_key: str) -> tuple[str | None, str | None]:
            stat = next((s for s in stats_pool if s["key"] == stat_key), None)
            if stat is None:
                return None, None
            this = stat["this"]
            higher_better = stat["higher_better"]
            l20_avg = stat["l20_avg"]
            bench_val = stat["bench"]
            l20_line = None
            if l20_avg is not None:
                delta = abs(int(round(this - l20_avg)))
                beats_l20 = this < l20_avg if not higher_better else this > l20_avg
                word = "better" if beats_l20 else "worse"
                l20_line = f"{delta} {word} than your last 20 rounds"
            bench_line = None
            if bench_val is not None and hi is not None:
                delta = abs(int(round(this - bench_val)))
                beats_bench = this < bench_val if not higher_better else this > bench_val
                word = "better" if beats_bench else "worse"
                bench_line = f"{delta} {word} than other {int(hi)} handicaps"
            return l20_line, bench_line

        bests = calc_personal_bests(all_prior, {})

        if bests["best_diff"] is not None and this_diff is not None and this_diff < bests["best_diff"]:
            if len(selected) < max_blocks:
                l20_line, bench_line = _ctx_lines("diff")
                selected.append({
                    "key": "diff",
                    "value": f"{this_diff:.1f}",
                    "label": "Personal Best · Differential",
                    "l20_line": l20_line,
                    "bench_line": bench_line,
                    "is_record": True,
                })

        if has_details and len(round_data.get("holes", {})) == 18:
            holes = round_data.get("holes", {})

            try:
                this_gross = sum(int(h["gross"]) for h in holes.values() if h.get("gross"))
            except (ValueError, TypeError):
                this_gross = None
            if bests["best_gross"] is not None and this_gross is not None and this_gross < bests["best_gross"]:
                if len(selected) < max_blocks:
                    selected.append({
                        "key": "gross",
                        "value": str(this_gross),
                        "label": "Personal Best · Gross Score",
                        "l20_line": None,
                        "bench_line": None,
                        "is_record": True,
                    })

            this_fir_count = _fir_count(holes)
            if bests["most_fir"] is not None and this_fir_count > bests["most_fir"]:
                if len(selected) < max_blocks:
                    l20_line, bench_line = _ctx_lines("fir")
                    selected.append({
                        "key": "fir",
                        "value": str(this_fir_count),
                        "label": "Personal Best · Fairways Hit",
                        "l20_line": l20_line,
                        "bench_line": bench_line,
                        "is_record": True,
                    })

            this_gir_count = _gir_count(holes)
            if bests["most_gir"] is not None and this_gir_count > bests["most_gir"]:
                if len(selected) < max_blocks:
                    l20_line, bench_line = _ctx_lines("gir")
                    selected.append({
                        "key": "gir",
                        "value": str(this_gir_count),
                        "label": "Personal Best · Greens in Regulation",
                        "l20_line": l20_line,
                        "bench_line": bench_line,
                        "is_record": True,
                    })

            this_putt_count = _putt_total(holes)
            if bests["fewest_putts"] is not None and this_putt_count > 0 and this_putt_count < bests["fewest_putts"]:
                if len(selected) < max_blocks:
                    l20_line, bench_line = _ctx_lines("putts")
                    selected.append({
                        "key": "putts",
                        "value": str(this_putt_count),
                        "label": "Personal Best · Fewest Putts",
                        "l20_line": l20_line,
                        "bench_line": bench_line,
                        "is_record": True,
                    })

        if has_details:
            holes = round_data.get("holes", {})
            if any(d.get("gross") == "1" for d in holes.values()):
                if len(selected) < max_blocks:
                    selected.append({
                        "value": "1",
                        "label": "Hole in One",
                        "l20_line": None,
                        "bench_line": None,
                    })

        selected_keys = {b["key"] for b in selected if "key" in b}

        for stat in stats_pool:
            if len(selected) >= max_blocks:
                break
            if stat["key"] in selected_keys:
                continue
            this = stat["this"]
            higher_better = stat["higher_better"]
            l20_avg = stat["l20_avg"]
            bench_val = stat["bench"]

            beats_l20 = l20_avg is not None and (this < l20_avg if not higher_better else this > l20_avg)
            beats_bench = bench_val is not None and hi is not None and (this < bench_val if not higher_better else this > bench_val)

            if not beats_l20 and not beats_bench:
                continue

            l20_line = None
            if l20_avg is not None:
                delta = abs(int(round(this - l20_avg)))
                word = "better" if beats_l20 else "worse"
                l20_line = f"{delta} {word} than your last 20 rounds"

            bench_line = None
            if bench_val is not None and hi is not None:
                delta = abs(int(round(this - bench_val)))
                word = "better" if beats_bench else "worse"
                bench_line = f"{delta} {word} than other {int(hi)} handicaps"

            selected.append({
                "value": stat["fmt"](this),
                "label": stat["label"],
                "l20_line": l20_line,
                "bench_line": bench_line,
            })

        return selected

    def action_continue_(self) -> None:
        if self._has_details:
            from screens.report_card import ReportCardScreen
            _log.info("screen: report card (from acknowledgment)")
            self.app.switch_screen(ReportCardScreen(self._round, from_entry=True))
        else:
            from screens.round_entry import _format_save_note
            note = _format_save_note(self._round)
            self.app.refresh_dashboard(save_note=note)
            self.app.pop_screen()
