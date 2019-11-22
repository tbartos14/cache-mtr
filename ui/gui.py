import sys
import time
from typing import List, Dict, Union
from math import log10

import numpy as np

from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.figure import Figure

from main import EvaluationDriver
from config import (
    DEFAULT_CACHE_SIZE,
    DEFAULT_NUM_OF_FILES,
    DEFAULT_REQUEST_NUM,
    DEFAULT_USER_NUM,
    DEFAULT_ALPHA_END,
    DEFAULT_ALPHA_START,
    DEFAULT_NUMBER_OF_ALPHA,
    DEFAULT_ZIPF,
    DEFAULT_SIMULATIONS_PER_TICK,
)

if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas,
        NavigationToolbar2QT as NavigationToolbar,
    )
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas,
        NavigationToolbar2QT as NavigationToolbar,
    )

global qapp


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):

        self.running: bool = False
        self.beta: float = 0
        self.range_alpha: List = []
        self.hide_alpha_zero: bool = False
        self.need_to_remake: bool = True
        self.ready_to_go = False
        self.logarithmic = False
        self.simulations_per_tick: int = 0

        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        # layout = QtWidgets.QVBoxLayout(self._main)
        layout = QtWidgets.QGridLayout(self._main)

        self.setWindowTitle("Caching Algorithm Simulation")

        self.static_canvas = FigureCanvas(Figure(figsize=(6, 4)))
        layout.addWidget(self.static_canvas, 0, 0)
        # self.addToolBar(NavigationToolbar(static_canvas, self))

        self.dynamic_canvas = FigureCanvas(Figure(figsize=(6, 4)))
        layout.addWidget(self.dynamic_canvas, 1, 0)
        # self.addToolBar(QtCore.Qt.BottomToolBarArea,
        #                 NavigationToolbar(dynamic_canvas, self))

        self.file_distribution = FigureCanvas(Figure(figsize=(6, 4)))
        layout.addWidget(self.file_distribution, 0, 1)

        self._file_dist = self.file_distribution.figure.subplots()

        # mini UI layout for button input
        entry_corner = QtWidgets.QGridLayout(self._main)
        layout.addLayout(entry_corner, 1, 1)
        miniui = QtWidgets.QGridLayout(self._main)
        entry_corner.addLayout(miniui, 0, 0)

        start_stop = QtWidgets.QGridLayout(self._main)
        miniui.addLayout(start_stop, 0, 0)

        entry_text = QtWidgets.QGridLayout(self._main)
        entry_corner.addLayout(entry_text, 0, 1)

        self.toggle_button = QtWidgets.QPushButton("Run")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setFixedWidth(80)
        self.toggle_button.toggled.connect(self.toggle_run)

        self.restart_button = QtWidgets.QPushButton("Restart")
        self.restart_button.setFixedWidth(80)
        self.restart_button.clicked.connect(self._flag_for_restart)

        start_stop.addWidget(self.toggle_button, 0, 0)
        start_stop.addWidget(self.restart_button, 1, 0)

        # checkboxes
        self.toggle_buttons = QtWidgets.QGridLayout(self._main)
        miniui.addLayout(self.toggle_buttons, 1, 0)

        self.box_hide_alpha_zero = QtWidgets.QCheckBox(
            "Hide \\alpha=0/Show \\alpha=1", self
        )
        self.box_hide_alpha_zero.stateChanged.connect(self.clicked_hide_a)
        self.toggle_buttons.addWidget(self.box_hide_alpha_zero, 0, 0)

        # needs_restart_label = QtWidgets.QLabel("Requires Restart")
        # self.toggle_buttons.addWidget(needs_restart_label, 1, 0)
        self.is_logarithmic = QtWidgets.QCheckBox("Logarithmic \\alpha")
        self.is_logarithmic.stateChanged.connect(self.clicked_logarithmic)
        self.toggle_buttons.addWidget(self.is_logarithmic, 2, 0)

        # entries
        user_num_label = QtWidgets.QLabel("Number of Users")
        entry_text.addWidget(user_num_label, 0, 0)
        self.user_num_entry = QtWidgets.QLineEdit(self)
        self.user_num_entry.setFixedWidth(80)
        entry_text.addWidget(self.user_num_entry, 1, 0)

        file_num_label = QtWidgets.QLabel("Number of Files")
        entry_text.addWidget(file_num_label, 2, 0)
        self.file_num_entry = QtWidgets.QLineEdit(self)
        self.file_num_entry.setFixedWidth(80)
        entry_text.addWidget(self.file_num_entry, 3, 0)

        cache_size_label = QtWidgets.QLabel("Cached Files / User")
        entry_text.addWidget(cache_size_label, 4, 0)
        self.cache_size_entry = QtWidgets.QLineEdit(self)
        self.cache_size_entry.setFixedWidth(80)
        entry_text.addWidget(self.cache_size_entry, 5, 0)

        requested_size_label = QtWidgets.QLabel("Requested Files / User")
        entry_text.addWidget(requested_size_label, 6, 0)
        self.requested_size_entry = QtWidgets.QLineEdit(self)
        self.requested_size_entry.setFixedWidth(80)
        entry_text.addWidget(self.requested_size_entry, 7, 0)

        alpha_start_label = QtWidgets.QLabel("\\alpha Start")
        entry_text.addWidget(alpha_start_label, 0, 1)
        self.alpha_start_entry = QtWidgets.QLineEdit(self)
        self.alpha_start_entry.setFixedWidth(80)
        entry_text.addWidget(self.alpha_start_entry, 1, 1)

        alpha_end_label = QtWidgets.QLabel("\\alpha End")
        entry_text.addWidget(alpha_end_label, 2, 1)
        self.alpha_end_entry = QtWidgets.QLineEdit(self)
        self.alpha_end_entry.setFixedWidth(80)
        entry_text.addWidget(self.alpha_end_entry, 3, 1)

        num_of_alpha_label = QtWidgets.QLabel("# d\\alpha Simulations")
        entry_text.addWidget(num_of_alpha_label, 4, 1)
        self.num_of_alpha_entry = QtWidgets.QLineEdit(self)
        self.num_of_alpha_entry.setFixedWidth(80)
        entry_text.addWidget(self.num_of_alpha_entry, 5, 1)

        zipf_label = QtWidgets.QLabel("Zipf constant a")
        entry_text.addWidget(zipf_label, 6, 1)
        self.zipf_entry = QtWidgets.QLineEdit(self)
        self.zipf_entry.setFixedWidth(80)
        entry_text.addWidget(self.zipf_entry, 7, 1)

        simulation_ptick_label = QtWidgets.QLabel("Simulations per tick")
        entry_text.addWidget(simulation_ptick_label, 8, 0)
        self.simulation_ptick_entry = QtWidgets.QLineEdit(self)
        self.simulation_ptick_entry.setFixedWidth(80)
        entry_text.addWidget(self.simulation_ptick_entry, 9, 0)

        self._static_ax = self.static_canvas.figure.subplots()

        self._dynamic_ax = self.dynamic_canvas.figure.subplots()
        self._timer = self.dynamic_canvas.new_timer(
            100, [(self._update_canvas, (), {})]
        )

        # set box data manually
        self.user_num_entry.setText(str(DEFAULT_USER_NUM))
        self.file_num_entry.setText(str(DEFAULT_NUM_OF_FILES))
        self.cache_size_entry.setText(str(DEFAULT_CACHE_SIZE))
        self.requested_size_entry.setText(str(DEFAULT_REQUEST_NUM))
        self.alpha_start_entry.setText(str(DEFAULT_ALPHA_START))
        self.alpha_end_entry.setText(str(DEFAULT_ALPHA_END))
        self.num_of_alpha_entry.setText(str(DEFAULT_NUMBER_OF_ALPHA))
        self.zipf_entry.setText(str(DEFAULT_ZIPF))
        self.simulation_ptick_entry.setText(str(DEFAULT_SIMULATIONS_PER_TICK))

    def initialize_simulation(self):

        # pull data from boxes to determine initialization
        need_to_bail: bool = False

        entries_dict = {
            "user_num": [self.user_num_entry, int],
            "file_num": [self.file_num_entry, int],
            "cache_size": [self.cache_size_entry, int],
            "request_size": [self.requested_size_entry, int],
            "alpha_start": [self.alpha_start_entry, float],
            "alpha_end": [self.alpha_end_entry, float],
            "num_alpha": [self.num_of_alpha_entry, int],
            "file_zipf_scalar": [self.zipf_entry, float],
            "sim_per_tick": [self.simulation_ptick_entry, int],
        }

        result_dict: Dict[str, Union[int, float]] = dict()

        for key, value in entries_dict.items():
            try:
                intermediate = value[0].text()
                finished = value[1](intermediate)
                result_dict[key] = finished
            except Exception as e:
                need_to_bail = True
                value[0].setText("")
        if need_to_bail:
            self.ready_to_go = False
            return

        if self.logarithmic:
            self.range_alpha = np.linspace(
                log10(result_dict["alpha_start"]),
                log10(result_dict["alpha_end"]),
                result_dict["num_alpha"],
            )
            self.range_alpha = np.power(10, self.range_alpha)
        else:
            self.range_alpha = np.linspace(
                result_dict["alpha_start"],
                result_dict["alpha_end"],
                result_dict["num_alpha"],
            )

        self.simulations_per_tick = result_dict["sim_per_tick"]

        self.range_alpha = list(self.range_alpha)

        # setup evaluation driver
        self.evaluators = []
        for alpha in self.range_alpha:
            evaluator = EvaluationDriver(
                num_of_files=result_dict["file_num"],
                cache_size=result_dict["cache_size"],
                num_of_users=result_dict["user_num"],
                num_of_requests=result_dict["request_size"],
                alpha=alpha,
                zipf_constant=result_dict["file_zipf_scalar"],
            )
            evaluator.setup()
            self.evaluators.append(evaluator)

        self.x_axis = self.evaluators[0].index_files()
        self.draw_dist()
        self._timer.start()
        self.ready_to_go = True

    def _flag_for_restart(self):
        self._timer.stop()
        self.running = False
        self.toggle_button.setChecked(False)
        qapp.processEvents()
        self.need_to_remake = True
        self._dynamic_ax.clear()
        self._dynamic_ax.figure.canvas.draw()
        self._static_ax.clear()
        self._static_ax.figure.canvas.draw()

    def _update_canvas(self):

        if self.running:
            import time

            t1 = time.time()
            self._dynamic_ax.clear()
            [
                evaluator.drive_multiple(self.simulations_per_tick)
                for evaluator in self.evaluators
            ]
            t2 = time.time()

            print(f"Differential: {t2-t1}")

            avgs = [
                sum(evaluator.trials) / len(evaluator.trials)
                for evaluator in self.evaluators
            ]
            maxs = [
                max(evaluator.trials) / evaluator.num_of_users
                for evaluator in self.evaluators
            ]
            mins = [
                min(evaluator.trials) / evaluator.num_of_users
                for evaluator in self.evaluators
            ]
            adjusted_average = [
                sum(evaluator.trials) / len(evaluator.trials) / evaluator.num_of_users
                for evaluator in self.evaluators
            ]

            self._dynamic_ax.plot(self.range_alpha, avgs)
            self._dynamic_ax.figure.tight_layout()
            self._dynamic_ax.set_ylim(ymin=0, ymax=1.5 * (max(avgs)))
            self._dynamic_ax.set_ylabel("Transaction Cost")
            if self.logarithmic:
                self._dynamic_ax.set_xlabel("\\alpha (log)")
                self._dynamic_ax.set_xscale("log")
            else:
                self._dynamic_ax.set_xlabel("\\alpha (log)")
                self._dynamic_ax.set_xscale("linear")
            self._dynamic_ax.figure.tight_layout()
            self._dynamic_ax.figure.canvas.draw()

            # now deal with min/max
            self._static_ax.clear()
            self._static_ax.plot(self.range_alpha, maxs)
            self._static_ax.plot(self.range_alpha, mins)
            self._static_ax.plot(self.range_alpha, adjusted_average)
            self._static_ax.set_ylabel("Transaction Cost per User")
            if self.logarithmic:
                self._static_ax.set_xlabel("\\alpha (log)")
                self._static_ax.set_xscale("log")
            else:
                self._static_ax.set_xlabel("\\alpha (log)")
                self._static_ax.set_xscale("linear")
            self._static_ax.figure.tight_layout()
            self._static_ax.figure.canvas.draw()

    def toggle_run(self) -> None:
        self.running = self.toggle_button.isChecked()
        if self.running:
            if self.need_to_remake:
                self.initialize_simulation()
            if self.ready_to_go:
                self._timer.start()
            else:
                self._flag_for_restart()
        else:
            self._timer.stop()
        qapp.processEvents()

    def clicked_hide_a(self, state):
        self.hide_alpha_zero = state == QtCore.Qt.Checked
        self.draw_dist()

    def clicked_logarithmic(self, state):
        self.logarithmic = state == QtCore.Qt.Checked
        self.need_to_remake = True

    def draw_dist(self):
        self._file_dist.clear()
        self._file_dist.plot(self.x_axis, self.evaluators[0].pm.file_distribution)

        if self.hide_alpha_zero:
            if 0 in self.range_alpha:
                for index in range(len(self.range_alpha)):
                    if 1 in self.range_alpha:
                        if (
                            self.range_alpha.index(0) != index
                            and self.range_alpha.index(1) != index
                        ):
                            self._file_dist.plot(
                                self.x_axis, self.evaluators[index].cm.cache_p_choice
                            )
                    else:
                        if self.range_alpha.index(0) != index:
                            self._file_dist.plot(
                                self.x_axis, self.evaluators[index].cm.cache_p_choice
                            )
        else:
            if 1 in self.range_alpha:
                for index in range(len(self.range_alpha)):
                    if self.range_alpha.index(1) != index:
                        self._file_dist.plot(
                            self.x_axis, self.evaluators[index].cm.cache_p_choice
                        )
            else:
                for index in range(len(self.range_alpha)):
                    self._file_dist.plot(
                        self.x_axis, self.evaluators[index].cm.cache_p_choice
                    )

        self._file_dist.legend(["Original P_r(m)"])
        self._file_dist.set_xlabel("File Index (m)")
        self._file_dist.set_ylabel("Probability")
        self._file_dist.set_ylim(ymin=0)
        self._file_dist.figure.tight_layout()
        self._file_dist.figure.canvas.draw()


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    app.show()
    qapp.exec_()
