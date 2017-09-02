from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QGridLayout, QGroupBox, QVBoxLayout, QDialogButtonBox
from gui.components.LabelledCombobox import LabelledCombobox
from gui.components.LabelledCheckbox import LabelledCheckbox
from gui.components.LabelledDoubleSpinBox import LabelledDoubleSpinBox
from gui.components.LabelledSpinBox import LabelledSpinBox
from gui.components.ColourBox import ColourBox
from gui.components.FontComboBox import FontComboBox

from current.default_config import defaults
from gui.gui_utils import font_weights
from functools import partial



class TitrationPlotPopup(QDialog):

    def __init__(self, parent=None, variables=None, **kw):
        super(TitrationPlotPopup, self).__init__(parent)
        self.setWindowTitle("Titration Plot Settings")
        grid = QGridLayout()
        grid.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(grid)
        self.variables = None
        if variables:
            self.variables = variables["titration_plot_settings"]
        self.default = defaults["titration_plot_settings"]

        self.tplot_subtitle_groupbox = QGroupBox()
        self.tplot_subtitle_groupbox_layout = QVBoxLayout()
        self.tplot_subtitle_groupbox.setLayout(self.tplot_subtitle_groupbox_layout)
        self.tplot_subtitle_groupbox.setTitle("Subtitle Settings")
        self.tplot_subtitle_fn = FontComboBox(self, "Subtitle Font")
        self.tplot_subtitle_fs = LabelledSpinBox(self, "Subtitle Font Size")
        self.tplot_subtitle_pad = LabelledDoubleSpinBox(self, "Subtitle Padding")
        self.tplot_subtitle_weight = LabelledCombobox(self, text="Subtitle Font Weight", items=font_weights)

        self.tplot_x_label_groupbox = QGroupBox()
        self.tplot_x_label_groupbox_layout = QVBoxLayout()
        self.tplot_x_label_groupbox.setLayout(self.tplot_x_label_groupbox_layout)
        self.tplot_x_label_groupbox.setTitle("X Label Settings")

        self.tplot_x_label_fn = FontComboBox(self, "X Font Label")
        self.tplot_x_label_fs = LabelledSpinBox(self, "X Label Font Size")
        self.tplot_x_label_pad = LabelledSpinBox(self, "X Label Padding")
        self.tplot_x_label_weight = LabelledCombobox(self, text="X Label Font Weight", items=font_weights)

        self.tplot_y_label_groupbox = QGroupBox()
        self.tplot_y_label_groupbox_layout = QVBoxLayout()
        self.tplot_y_label_groupbox.setLayout(self.tplot_y_label_groupbox_layout)
        self.tplot_y_label_groupbox.setTitle("Y Label Settings")

        self.tplot_y_tick_groupbox = QGroupBox()
        self.tplot_y_tick_groupbox_layout = QVBoxLayout()
        self.tplot_y_tick_groupbox.setLayout(self.tplot_y_tick_groupbox_layout)
        self.tplot_y_tick_groupbox.setTitle("Tick Settings")

        self.tplot_y_label_fn = FontComboBox(self, "Y Label Font")
        self.tplot_y_label_fs = LabelledSpinBox(self, "Y Label Font Size")
        self.tplot_y_label_pad = LabelledSpinBox(self, "Y Label Padding")
        self.tplot_y_label_weight = LabelledCombobox(self, text="Y Label Font Weight", items=font_weights)

        self.tplot_x_ticks_pad = LabelledSpinBox(self, "X Tick Padding")
        self.tplot_x_ticks_len = LabelledSpinBox(self, "X Tick Length")

        self.tplot_y_ticks_fn = FontComboBox(self, "Y Tick Font")
        self.tplot_y_ticks_fs = LabelledSpinBox(self, "Y Tick Font Size")
        self.tplot_y_ticks_rot = LabelledSpinBox(self, "Y Tick Rotation")
        self.tplot_y_ticks_pad = LabelledDoubleSpinBox(self, "Y Tick Padding")
        self.tplot_y_ticks_weight = LabelledCombobox(self, text="Y Tick Font Weight", items=font_weights)
        self.tplot_y_ticks_len = LabelledDoubleSpinBox(self, "Y Tick Length")
        self.tplot_y_grid_flag = LabelledCheckbox(self, "Show Y Grid")
        self.tplot_y_grid_color = ColourBox(self, "Y Grid Colour")
        self.tplot_y_grid_linestyle = LabelledCombobox(self, text="Y Grid Line Style", items=['-', '--', '-.', ':'])
        self.tplot_y_grid_linewidth = LabelledDoubleSpinBox(self, "Y Grid Line Width")
        self.tplot_y_grid_alpha = LabelledDoubleSpinBox(self, "Y Grid Alpha", min=0, max=1, step=0.1)
        self.tplot_vspace = LabelledDoubleSpinBox(self, "Plot Vertical Spacing")



        self.tplot_subtitle_groupbox.layout().addWidget(self.tplot_subtitle_fn)
        self.tplot_subtitle_groupbox.layout().addWidget(self.tplot_subtitle_fs)
        self.tplot_subtitle_groupbox.layout().addWidget(self.tplot_subtitle_pad)
        self.tplot_subtitle_groupbox.layout().addWidget(self.tplot_subtitle_weight)

        self.tplot_x_label_groupbox.layout().addWidget(self.tplot_x_label_fn)
        self.tplot_x_label_groupbox.layout().addWidget(self.tplot_x_label_fs)
        self.tplot_x_label_groupbox.layout().addWidget(self.tplot_x_label_pad)
        self.tplot_x_label_groupbox.layout().addWidget(self.tplot_x_label_weight)



        self.layout().addWidget(self.tplot_subtitle_groupbox, 0, 0, 4, 1)
        self.layout().addWidget(self.tplot_x_label_groupbox, 0, 1, 4, 1)


        self.tplot_y_label_groupbox.layout().addWidget(self.tplot_y_label_fn)
        self.tplot_y_label_groupbox.layout().addWidget(self.tplot_y_label_fs)
        self.tplot_y_label_groupbox.layout().addWidget(self.tplot_y_label_weight)
        self.tplot_y_label_groupbox.layout().addWidget(self.tplot_y_label_pad)

        self.layout().addWidget(self.tplot_y_label_groupbox, 4, 1, 4, 1)

        # self.layout().addWidget(self.tplot_y_label_weight, 4, 1)
        self.tplot_y_tick_groupbox.layout().addWidget(self.tplot_x_ticks_pad)
        self.tplot_y_tick_groupbox.layout().addWidget(self.tplot_x_ticks_len)
        self.tplot_y_tick_groupbox.layout().addWidget(self.tplot_y_ticks_fn)
        self.tplot_y_tick_groupbox.layout().addWidget(self.tplot_y_ticks_fs,)
        self.tplot_y_tick_groupbox.layout().addWidget(self.tplot_y_ticks_rot)
        self.tplot_y_tick_groupbox.layout().addWidget(self.tplot_y_ticks_pad)
        self.tplot_y_label_groupbox.layout().addWidget(self.tplot_y_ticks_weight)
        self.tplot_y_label_groupbox.layout().addWidget(self.tplot_y_ticks_len)

        self.layout().addWidget(self.tplot_y_tick_groupbox, 4, 0, 4, 1)

        self.tplot_y_grid_groupbox = QGroupBox()
        self.tplot_y_grid_groupbox_layout = QVBoxLayout()
        self.tplot_y_grid_groupbox.setLayout(self.tplot_y_grid_groupbox_layout)
        self.tplot_y_grid_groupbox.setTitle("Y Grid Settings")

        self.tplot_y_grid_groupbox.layout().addWidget(self.tplot_y_grid_flag)
        self.tplot_y_grid_groupbox.layout().addWidget(self.tplot_y_grid_color)
        self.tplot_y_grid_groupbox.layout().addWidget(self.tplot_y_grid_linestyle)
        self.tplot_y_grid_groupbox.layout().addWidget(self.tplot_y_grid_linewidth)
        self.tplot_y_grid_groupbox.layout().addWidget(self.tplot_y_grid_alpha)
        self.tplot_y_grid_groupbox.layout().addWidget(self.tplot_vspace)

        self.layout().addWidget(self.tplot_y_grid_groupbox, 0, 2, 4, 1)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults)

        self.buttonBox.accepted.connect(partial(self.set_values, variables))
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.get_defaults)

        self.layout().addWidget(self.buttonBox, 8, 2, 1, 1)

        if variables:
            self.get_values()

    def get_defaults(self):
        self.tplot_subtitle_fn.select(self.default["tplot_subtitle_fn"])
        self.tplot_subtitle_fs.setValue(self.default["tplot_subtitle_fs"])
        self.tplot_subtitle_weight.select(self.default["tplot_subtitle_weight"])
        self.tplot_subtitle_pad.setValue(self.default["tplot_subtitle_pad"])
        self.tplot_x_label_fn.select(self.default["tplot_x_label_fn"])
        self.tplot_x_label_fs.setValue(self.default["tplot_x_label_fs"])
        self.tplot_x_label_pad.setValue(self.default["tplot_x_label_pad"])
        self.tplot_x_label_weight.select(self.default["tplot_x_label_weight"])
        self.tplot_y_label_fn.select(self.default["tplot_y_label_fn"])
        self.tplot_y_label_fs.setValue(self.default["tplot_y_label_fs"])
        self.tplot_y_label_pad.setValue(self.default["tplot_y_label_pad"])
        self.tplot_y_label_weight.select(self.default["tplot_y_label_weight"])
        self.tplot_x_ticks_pad.setValue(self.default["tplot_x_ticks_pad"])
        self.tplot_x_ticks_len.setValue(self.default["tplot_x_ticks_len"])

        self.tplot_y_ticks_fn.select(self.default["tplot_y_ticks_fn"])
        self.tplot_y_ticks_fs.setValue(self.default["tplot_y_ticks_fs"])
        self.tplot_y_ticks_rot.setValue(self.default["tplot_y_ticks_rot"])
        self.tplot_y_ticks_pad.setValue(self.default["tplot_y_ticks_pad"])
        self.tplot_y_ticks_weight.select(self.default["tplot_y_ticks_weight"])
        self.tplot_y_ticks_len.setValue(self.default["tplot_y_ticks_len"])
        self.tplot_y_grid_flag.setChecked(self.default["tplot_y_grid_flag"])
        self.tplot_y_grid_color.select(self.default["tplot_y_grid_color"])
        self.tplot_y_grid_linestyle.select(self.default["tplot_y_grid_linestyle"])
        self.tplot_y_grid_linewidth.setValue(self.default["tplot_y_grid_linewidth"])
        self.tplot_y_grid_alpha.setValue(self.default["tplot_y_grid_alpha"])


    def set_values(self, variables):
        self.variables["tplot_subtitle_fn"] = str(self.tplot_subtitle_fn.fields.currentText())
        self.variables["tplot_subtitle_fs"] = self.tplot_subtitle_fs.field.value()
        self.variables["tplot_subtitle_pad"] = self.tplot_subtitle_pad.field.value()
        self.variables["tplot_subtitle_weight"] = str(self.tplot_subtitle_weight.fields.currentText())
        self.variables["tplot_x_label_fn"] = str(self.tplot_x_label_fn.fields.currentText())
        self.variables["tplot_x_label_fs"] = self.tplot_x_label_fs.field.value()
        self.variables["tplot_x_label_pad"] = self.tplot_x_label_pad.field.value()
        self.variables["tplot_x_label_weight"] = str(self.tplot_x_label_weight.fields.currentText())
        self.variables["tplot_y_label_fn"] = str(self.tplot_y_label_fn.fields.currentText())
        self.variables["tplot_y_label_fs"] = self.tplot_y_label_fs.field.value()
        self.variables["tplot_y_label_pad"] = self.tplot_y_label_pad.field.value()
        self.variables["tplot_y_label_weight"] = str(self.tplot_y_label_weight.fields.currentText())

        self.variables["tplot_x_ticks_pad"] = self.tplot_x_ticks_pad.field.value()
        self.variables["tplot_x_ticks_len"] = self.tplot_x_ticks_len.field.value()

        self.variables["tplot_y_ticks_fn"] = str(self.tplot_y_ticks_fn.fields.currentText())
        self.variables["tplot_y_ticks_fs"] = self.tplot_y_ticks_fs.field.value()
        self.variables["tplot_y_ticks_rot"] = self.tplot_y_ticks_rot.field.value()
        self.variables["tplot_y_ticks_pad"] = self.tplot_y_ticks_pad.field.value()

        self.variables["tplot_y_ticks_weight"] = str(self.tplot_y_ticks_weight.fields.currentText())
        self.variables["tplot_y_ticks_len"] = self.tplot_y_ticks_len.field.value()
        self.variables["tplot_y_grid_flag"] = self.tplot_y_grid_flag.checkBox.isChecked()
        self.variables["tplot_y_grid_color"] = str(self.tplot_y_grid_color.fields.currentText())
        self.variables["tplot_y_grid_linestyle"] = str(self.tplot_y_grid_linestyle.fields.currentText())
        self.variables["tplot_y_grid_linewidth"] = self.tplot_y_grid_linewidth.field.value()
        self.variables["tplot_y_grid_alpha"] = self.tplot_y_grid_alpha.field.value()

        variables["tplot_settings"] = self.variables
        self.accept()

    def get_values(self):
        self.tplot_subtitle_fn.select(self.variables["tplot_subtitle_fn"])
        self.tplot_subtitle_fs.setValue(self.variables["tplot_subtitle_fs"])
        self.tplot_subtitle_weight.select(self.variables["tplot_subtitle_weight"])
        self.tplot_subtitle_pad.setValue(self.variables["tplot_subtitle_pad"])
        self.tplot_x_label_fn.select(self.variables["tplot_x_label_fn"])
        self.tplot_x_label_fs.setValue(self.variables["tplot_x_label_fs"])
        self.tplot_x_label_pad.setValue(self.variables["tplot_x_label_pad"])
        self.tplot_x_label_weight.select(self.variables["tplot_x_label_weight"])
        self.tplot_y_label_fn.select(self.variables["tplot_y_label_fn"])
        self.tplot_y_label_fs.setValue(self.variables["tplot_y_label_fs"])
        self.tplot_y_label_pad.setValue(self.variables["tplot_y_label_pad"])
        self.tplot_y_label_weight.select(self.variables["tplot_y_label_weight"])
        self.tplot_x_ticks_pad.setValue(self.variables["tplot_x_ticks_pad"])
        self.tplot_x_ticks_len.setValue(self.variables["tplot_x_ticks_len"])

        self.tplot_y_ticks_fn.select(self.variables["tplot_y_ticks_fn"])
        self.tplot_y_ticks_fs.setValue(self.variables["tplot_y_ticks_fs"])
        self.tplot_y_ticks_rot.setValue(self.variables["tplot_y_ticks_rot"])
        self.tplot_y_ticks_pad.setValue(self.variables["tplot_y_ticks_pad"])
        self.tplot_y_ticks_weight.select(self.variables["tplot_y_ticks_weight"])
        self.tplot_y_ticks_len.setValue(self.variables["tplot_y_ticks_len"])
        self.tplot_y_grid_flag.setChecked(self.variables["tplot_y_grid_flag"])
        self.tplot_y_grid_color.select(self.variables["tplot_y_grid_color"])
        self.tplot_y_grid_linestyle.select(self.variables["tplot_y_grid_linestyle"])
        self.tplot_y_grid_linewidth.setValue(self.variables["tplot_y_grid_linewidth"])
        self.tplot_y_grid_alpha.setValue(self.variables["tplot_y_grid_alpha"])
