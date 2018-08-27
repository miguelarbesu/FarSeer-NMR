"""
Copyright © 2017-2018 Farseer-NMR
João M.C. Teixeira and Simon P. Skinner

@ResearchGate https://goo.gl/z8dPJU
@Twitter https://twitter.com/farseer_nmr

This file is part of Farseer-NMR.

Farseer-NMR is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Farseer-NMR is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Farseer-NMR. If not, see <http://www.gnu.org/licenses/>.

Optimal algorithm to run the Farseer-NMR method.

Usage as main script:

    python <path-to>/farseermain.py <path-to>/farseer-user-variables.py

Can be used as imported module. Contains several functions that aid in
managing the Farseer-NMR analysis routines.

Methods:
    .read_user_variables()
        .config_user_variables()
    .copy_Farseer_version()
    .log_time_stamp()
    .logs()
    .initial_checks()
    .checks_PRE_analysis_flags()
    .checks_cube_axes_flags()
    .checks_plotting_flags()
    .checks_calculation_flags()
    .checks_fit_input()
    .creates_farseer_dataset()
    .reads_peaklists()
    .inits_coords_names()
    .identify_residues()
    .correct_shifts()
    .fill_na()
    .expand_missing()
    .add_missing()
    .organize_columns()
    .init_fs_cube()
    .series_kwargs()
    .gen_series_dcts()
    .eval_series()
    .perform_calcs()
    .perform_fits()
    .PRE_analysis()
    .exports_series()
    .exports_chimera_att_files()
    .plots_data()
    .comparison_analysis_routines()
    .analyse_comparisons()
    .run_farseer()
"""

#  
#import logging
#import logging.config
import sys
import os
import shutil
import json
import datetime  # used to write the log file
import pandas as pd

#import core.fslibs.log_config as fslogconf
from core.fslibs.Logger import FarseerLogger
from core.fslibs import FarseerCube as fcube
from core.fslibs import FarseerSeries as fss
from core.fslibs import Comparisons as fsc
from core.fslibs.WetHandler import WetHandler as fsw

class FarseerNMR():
    """
    Handles Farseer-NMR interface
    """
    def __init__(self, fsuv):
        """
        Initiates the Farseer-NMR interface.
        
        Parameters:
            - fsuv (dict or str): 
                    - (str) path to JSON dictionary containing
                            all the user defined variables.
                    - (dict) Python dictionary containing all user defined
                            variables.
        """
        # reads user variables
        # this has to be done before starting logging system
        if isinstance(fsuv, str):
            if os.path.exists(fsuv):
                self.read_fsuv_json(fsuv)
            else:
                msg = "The path provided to JSON file does not exists."
                sys.exit(msg)
        elif isinstance(fsuv, dict):
            self.fsuv = fsuv
            self._updates_output_dir()
            self._config_user_variables()
        else:
            msg = "fsuv argument should be a dict or string path"
            sys.exit(msg)
        
        self._starts_logger()
        
        self._fsuv_integrity_checks()
    
    
    def _updates_output_dir(self):
        """
        Updates output path in fsuv dictionary.
        
        If output path already defined updates cwd to the output path.
        If not: updates output_path to os.getcwd()
        """
        
        if not self.fsuv["general_settings"]["output_path"]:
            self.change_current_dir(
                os.path.abspath(os.getcwd()),
                update_fsuv=True
                )
        else:
            self.change_current_dir(self.fsuv["general_settings"]["output_path"])
    
    def _starts_logger(self):
        """Initiates and assigns self.logger."""
        
        self.logger = FarseerLogger(
            __name__,
            self.fsuv["general_settings"]["output_path"]
            ).setup_log()
        
        self.logger.debug('logger initiated')
        
        return None
    
    def _config_user_variables(self):
        """
        Performs additional operations on the user defined json dictionary
        containing the FarseerNMR variables so it can be used properly.
        
        Returns:
            None
        """
        
        # alias .conf json file
        general = self.fsuv["general_settings"]
        fitting = self.fsuv["fitting_settings"]
        cs = self.fsuv["cs_settings"]
        csp = self.fsuv["csp_settings"]
        fasta = self.fsuv["fasta_settings"]
        plots_f1 = self.fsuv["PosF1_settings"]
        plots_f2 = self.fsuv["PosF2_settings"]
        plots_csp = self.fsuv["csp_settings"]
        plots_height = self.fsuv["Height_ratio_settings"]
        plots_volume = self.fsuv["Volume_ratio_settings"]
    
        # does the user want to perform any analysis on the Farseer-NMR cube?
        self.fsuv["any_axis"] = any([
            fitting["do_along_x"],
            fitting["do_along_y"],
            fitting["do_along_z"]
            ])
        
        # sorted values to be used as x coordinates in the fitting routine
        # self.fsuv.txv = sorted(self.fsuv.titration_x_values)
        
        # ORDERED names of the restraints that can be calculated
        self.fsuv["restraint_names"] = [
            plots_f1["calccol_name_PosF1_delta"],
            plots_f2["calccol_name_PosF2_delta"],
            plots_csp["calccol_name_CSP"],
            plots_height["calccol_name_Height_ratio"],
            plots_volume["calccol_name_Volume_ratio"]
            ]
        
        # ORDERED calculation restraints flags
        self.fsuv["restraint_flags"] = [
            plots_f1["calcs_PosF1_delta"],
            plots_f2["calcs_PosF2_delta"],
            plots_csp["calcs_CSP"],
            plots_height["calcs_Height_ratio"],
            plots_volume["calcs_Volume_ratio"]
            ]
        
        restraint_settings_dct = {
            'calcs_restraint_flg': self.fsuv["restraint_flags"],
            
            'plt_y_axis_lbl': [
                plots_f1["yy_label_PosF1_delta"],
                plots_f2["yy_label_PosF2_delta"],
                plots_csp["yy_label_CSP"],
                plots_height["yy_label_Height_ratio"],
                plots_volume["yy_label_Volume_ratio"]
                ],
            
            'plt_y_axis_scl': [
                (
                    -plots_f1["yy_scale_PosF1_delta"],
                    plots_f1["yy_scale_PosF1_delta"]
                    ),
                (
                    -plots_f2["yy_scale_PosF2_delta"],
                    plots_f2["yy_scale_PosF2_delta"]
                    ),
                (0, plots_csp["yy_scale_CSP"]),
                (0, plots_height["yy_scale_Height_ratio"]),
                (0, plots_volume["yy_scale_Volume_ratio"])
                ]
            }
        
        # A pd.DataFrame that organizes settings for each calculated restraint.
        # Index are the calculated params labels
        self.fsuv["restraint_settings"] = \
            pd.DataFrame(restraint_settings_dct, index=self.fsuv["restraint_names"])
        
        # does the user want to calculate any restraint?
        self.fsuv["calc_flags"] = any(self.fsuv["restraint_flags"])
        
        # does the user want to draw any plot?
        # self.fsuv.plotting_flags = any(
        
        # flags which self.fsuv.apply_PRE_analysis deppends on
        self.fsuv["PRE_analysis_flags"] = \
            fitting["do_along_z"] \
            and (plots_height["calcs_Height_ratio"] \
                or plots_volume["calcs_Volume_ratio"]) \
            and fitting["perform_comparisons"]
        
        ### configures flags for observables:
        #### provisional ****
        self.fsuv["obs_names"] = ['Position F1', 'Position F2', 'Height']
        observables_stngs_dict = {
            "obs_flags" : [
                self.fsuv["observables"]["plots_posf1"],
                self.fsuv["observables"]["plots_posf2"],
                self.fsuv["observables"]["plots_height"]
                ],
            
            "obs_yaxis_lbl" : ["1H (ppm)", "15N (ppm)", "Height"],
            
            "obs_yaxis_scl" : [
                self.fsuv["observables"]["posf1_scale"],
                self.fsuv["observables"]["posf2_scale"],
                self.fsuv["observables"]["height_scale"]
                ]
            }
        
        self.fsuv["observables_settings"] = \
            pd.DataFrame(observables_stngs_dict, index=self.fsuv["obs_names"])
        
        # adds nuclei Y axis limits for plots to the scatter flower
        # configuration dictionary
        self.fsuv["cs_scatter_flower_settings"]["xlim"] = \
            self.fsuv["PosF1_settings"]["yy_scale_PosF1_delta"]
        self.fsuv["cs_scatter_flower_settings"]["ylim"] = \
            self.fsuv["PosF2_settings"]["yy_scale_PosF2_delta"]
        
        return None
    
    def _fsuv_integrity_checks(self):
        """
        Performs integrity checks to confirm integrity between user defined
        variables. Warns the user with WETs if necessary.
        
        Returns: None
        """
        
        # PRE routines take only place at advanced stages of the 
        # Farseer-NMR calculation.
        # It would be a waste of time to have an error after 2h...
        if fsuv["pre_settings"]["apply_PRE_analysis"]:
            _checks_PRE_analysis_flags()
        
        return None
    
    def _checks_PRE_analysis_flags(self):
        """Checks flag compatibility in PRE Analysis routines."""
        
        # if all the flags upon which aplly_PRE_analysis depends on are
        # turned off:
        if not(self.fsuv["PRE_analysis_flags"]):
            msg = \
"PRE Analysis is set to <{}> and depends on the following variables: \
do_along_z :: <{}> || calcs_Height_ratio OR calcs_Volume_ratio :: <{}> || \
perform_comparisons :: <{}>. \
All these variables should be set to True for PRE Analysis to be executed.".\
                format(
                    self.fsuv["pre_settings"]["apply_PRE_analysis"],
                    self.fsuv["fitting_settings"]["do_along_z"],
                    self.fsuv["Height_ratio_settings"]["calcs_Height_ratio"] \
                        or self.fsuv["Volume_ratio_settings"]["calcs_Volume_ratio"],
                    self.fsuv["fitting_settings"]["perform_comparisons"]
                    )
            wet1 = fsw(msg_title='ERROR', msg=msg, wet_num=1)
            self.logger.info(wet1.wet)
            wet1.abort()
        
        return None
    
    def _checks_cube_axes_flags(self):
    """
    Checks if the user wants to perform any analysis
    on the Farseer-NMR Cube.
    
    Returns:
        - True if any analysis flag (X, Y or Z) is activate
        - False otherwise
    """
    
    if not(fsuv["any_axis"]):
        msg = \
"Analysis over X, Y or Z Farseer-NMR Cube's axes are all deactivated. \
There is nothing to calculate. Confirm this is actually what you want."
        wet2 = fsw(msg_title='NOTE', msg=msg, wet_num=2)
        self.logger.info(wet2.wet)
        return False
    
    else:
        return True
    
    def _log_state_stamp(self, state='STARTED', width=79):
        """
        Creates a time stamp for the log file.
        
        Parameters:
            - state (opt, str): the printed state
            - width (opt, int): the width of the stamp
        
        Returns: a state stamp
        """
        
        state_stamp = \
            '{0}  \n**LOG {2}:** {1} \n{0}  \n'.\
                format(
                    width*'*',
                    datetime.datetime.now().strftime("%c"),
                    state
                    )
        
        return state_stamp
    
    
    def change_current_dir(self, new_curr_dir, update_fsuv=False):
        """
        Changes running dir to path. Exists if path is not a valid directory.
        
        Parameters:
            - new_curr_dir (str): target directory
            - update_fsuv(opt, bool): updates self.fsuv "output_path" to
                new_curr_dir
            
        Returns: None
        """
        
        try:
            os.chdir(new_curr_dir)
        except NotADirectoryError as notdirerr: 
            msg = \
    """
    ***************************************
    *** The directory path does not exists
    *** {}
    ***
    {}
    ***************************************
    """.\
                format(notdirerr, how_to_run)
            sys.exit(msg)
        
        if update_fsuv:
            self.fsuv["general_settings"]["output_path"] = new_curr_dir
        
        
        return None
    
    def read_fsuv_json(self, fsuv_json_path):
        """
        Reads a JSON file containing the Farseer-NMR's user defined variables.
        
        Can be used to updated an existing configuration.
        
        Parameters:
            fsuv_json_path (str): path to the JSON file.
        
        Returns:
            None
        """
        
        how_to_run = """*** execute Farseer-NMR as
*** $ python <path_to>/farseermain.py <path_to_run_folder> <path_to_conf.json>"""
        
        # Reads json config absolute path
        json_cwd = os.path.abspath(fsuv_json_path)
        # loads and reads json config file
        try:
            self.fsuv = json.load(open(json_cwd, 'r'))
        except json.decoder.JSONDecodeError as jsonerror:
            msg = \
"""
***************************************
*** Error loading JSON file:
*** {}
*** {}
***************************************
""".\
                format(json_cwd, jsonerror)
            sys.exit(msg)
        except IsADirectoryError as direrr:
            msg = \
"""
***************************************
*** A directory was passed as argument instead of a json file.
*** {}
***
{}
***************************************
    """.\
                format(direrr, how_to_run)
            sys.exit(msg)
        
        self._updates_output_dir()
        
        # stores path to spectra/ folder
        self.fsuv["general_settings"]["input_spectra_path"] = \
            '{}/spectra'.format(self.fsuv["general_settings"]["output_path"])
        # stores path to json config file
        self.fsuv["general_settings"]["config_path"] = json_cwd
        # configs user variables necessary for Farseer-NMR
        
        self._config_user_variables()
        
        return None

    def copy_FarseerNMR_version(
            self,
            file_name='farseer_version',
            compress_type='zip'
            ):
        """
        Makes a copy of the running version.
        
        Parameters:
            file_name (str, opt): name of the compressed file
            compress_type (opt, str): extention of the compression file
                compatible with Python shutil.make_archive
                https://docs.python.org/3.6/library/shutil.html#shutil.make_archive
        
        Returns: None
        """
        
        script_wd = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            os.pardir
            )
        
        file_path = '{}/{}'.format(
            self.fsuv["general_settings"]["output_path"],
            file_name
            )
        
        try:
            shutil.make_archive(file_path, compress_type, script_wd)
        except ValueError as verror:
            msg = "Error while trying to export the Farseer-NMR version: {}".format(verror)
            wet36 = fsw(msg_title='WARNING', msg=msg, wet_num=36)
            self.logger.warning(wet36.wet)
            
            return None
        
        self.logger.info(
            'Farseer-NMR version exported correctly to {}.{}'.format(
                file_path,
                compress_type
                )
            )
        
        return None

def log_init(fsuv):
    """Operations performed when initializing the log file."""
    
    fout = fsuv["general_settings"]["logfile_name"]
    log_time_stamp(fout, mod='w')
    logs(
        "*** Run Calculation folder: {}\n".\
            format(fsuv["general_settings"]["output_path"]),
        fout
        )
    logs(
        "*** Config file: {}\n".\
            format(fsuv["general_settings"]["config_path"]),
        fout
        )
    
    return

def log_end(fsuv):
    """Operations performed when finalizing the log file."""
    
    print("*** Used JSON config file will be copied to the end of MD log file")
    fout = fsuv["general_settings"]["logfile_name"]
    logs(fsw(gen=False).end_well(), fout)
    log_time_stamp(fout, state='ENDED')
    logs("*** USED CONFIG FILE ***\n", fout, printit=False)
    fsuv_tmp = fsuv.copy()
    
    for key in fsuv.keys():
        if isinstance(fsuv_tmp[key], pd.DataFrame):
            fsuv_tmp.pop(key, None)
    
    with open(fsuv["general_settings"]["logfile_name"], 'a') as f:
        json.dump(fsuv_tmp, f, indent=4)
    
    return







def checks_plotting_flags(farseer_series, fsuv, resonance_type):
    """
    Checks whether any plotting flag is activated.
    
    Parameters:
        farseer_series (FarseerSeries instance): contains the
            experiments of the series.
        
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
        
        resonance_type (str): {'Backbone', 'Sidechains'}
     
    Returns:
        True if any plotting flag is activated,
        False otherwise.
    """
    
    plot_bool = pd.Series([v for k,v in fsuv["plotting_flags"].items()])
    
    # exports tables
    if not(plot_bool.any()):
        msg = \
"All potting flags are turned off. No plots will be drawn. \
Confirm in the Settings menu if this is the desired configuration. \
I won't leave you with empty hands though, all calculated restraints, \
NMR observables and user notes will be exported in nicely formatted tables ;-)"
        wet3 = fsw(msg_title='NOTE', msg=msg, wet_num=3)
        farseer_series.log_r(wet3.wet)
        return False
    
    return True

def checks_calculation_flags(fsuv):
    """
    Checks if the user wants to calculate any restraints.
    
    Parameters:
        fsuv (module): contains user defined variables (preferences) after
            .read_user_variables().
    """
    #WET#14
    if not(fsuv["calc_flags"]):
        msg = \
"All restraints calculation routines are deactivated. \
Nothing will be calculated."
        wet14 = fsw(msg_title='WARNING', msg=msg, wet_num=14)
        logs(wet14.wet, fsuv["general_settings"]["logfile_name"])
    
    return

def checks_fit_input(series, fsuv):
    """
    Checks whether required fit data and settings are provided correctly.
    
    Parameters:
        series (FarseerSeries instance):
        
        fsuv (module): contains user defined variables (preferences) after
            .read_user_variables().
    """

    x_values = fsuv["revo_settings"]["titration_x_values"]
    ######## WET#5, WET#6, WET#7
    if not(all([True if x>=0 else False for x in x_values])):
        msg = \
'There are negative values in titration_x_values variable. \
Fitting to the Hill Equation does not accept negative values. \
Please revisit your input'
        wet6 = fsw(msg_title='ERROR', msg=msg, wet_num=6)
        series.log_r(wet6.wet)
        series.abort()
    
    elif len(x_values) != len(series.items):
        msg = \
"The number of coordinate values defined for fitting/data respresentation, \
<fitting_x_values> variable [{}], do not match the number of data points \
along_x ,i.e. input peaklists. Please correct <fitting_x_values> variable or \
confirm you have not forgot any peaklist [{}].".\
            format(x_values, series.items)
        wet5 = fsw(msg_title='ERROR', msg=msg, wet_num=5)
        series.log_r(wet5.wet)
        series.abort()
    
    else:
        msg = \
"The number of coordinate values for data fitting along X axis equals the \
number of input peaklists, and no negative value was found. Data fit to the \
Hill Equation will be performed with the following values: {}.".\
            format(x_values)
        wet7 = fsw(msg_title='NOTE', msg=msg, wet_num=7)
        series.log_r(wet7.wet)
    
    return

def checks_axis_coherency(dim, fsuv):
    """
    Warns in case the axis the user activates for calculation actually
    has no data points to create a series.
    
    Parameters:
        dim (str): the dimension to warn about.
        
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
    
    Depends on:
    fsuv["general_settings"]["logfile_name"]
    """
    
    msg = \
'You have activated the analysis along dimension/axis {}. However, there are \
no datapoints along this axis so that a series could not be created and \
analysed. Confirm the axis analysis flags are correctly set in the Run \
Settings.'.\
        format(dim)    
    wet20 = fsw(msg_title='WARNING', msg=msg, wet_num=20)
    logs(wet20.wet, fsuv["general_settings"]["logfile_name"])
    
    return
    
def creates_farseer_dataset(fsuv):
    """
    Creates a Farseer-NMR dataset.
    
    Parameters:
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
    
    Returns:
        exp (FarseerCube class instance): contains all peaklist data.
    
    Depends on:
    fsuv["general_settings"]["input_spectra_path"]
    fsuv.has_sidechains
    fsuv.FASTAstart
    fsuv["general_settings"]["logfile_name"]
    """
    
    exp = fcube.FarseerCube(
        fsuv["general_settings"]["input_spectra_path"],
        has_sidechains=fsuv["general_settings"]["has_sidechains"],
        FASTAstart=fsuv["fasta_settings"]["FASTAstart"],
        applyFASTA=fsuv["fasta_settings"]["applyFASTA"]
        )
    exp.log_export_onthefly = True
    exp.log_export_name = fsuv["general_settings"]["logfile_name"]
    
    return exp

def reads_peaklists(exp, fsuv):
    """
    Loads Peaklist's Tree from spectra/ folder.
    
    Uses FarseerCube.load_experiments().
    
    Parameters:
        exp (FarseerCube class instance): contains all peaklist data.
        
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
    
    Depends on:
    fsuv.applyFASTA
    """
    
    exp.load_experiments()
    
    if fsuv["fasta_settings"]["applyFASTA"]:
        exp.load_experiments(filetype='.fasta')
    
    # even if the user does no want to analyse sidechains, Farseer-NMR
    # has to parse them out from the input peaklist if they exist
    if exp.has_sidechains:
        # str() is passed as a dummy function
        exp.load_experiments(resonance_type='Sidechains')
    
    return
    
def identify_residues(exp):
    """
    Reads Assignment information using FarseerCube.split_res_info().
    
    Parameters:
        exp (FarseerCube class instance): contains all peaklist data.
    """
    exp.split_res_info()
    
    return

def correct_shifts(
        exp, fsuv,
        resonance_type='Backbone'):
    """
    Corrects chemical shifts for all the peaklists to a reference peak
    in the (0,0,0) Farseer-NMR Cube coordinate.
    
    Uses FarseerCube.correct_shifts_*
    
    Parameters:
        exp (FarseerCube class instance): contains all peaklist data.
    
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
        
        resonance_type (str): {'Backbone', 'Sidechains'}
    
    Depends on:
    fsuv.cs_correction_res_ref
    """
    
    if resonance_type == 'Backbone':
        exp.correct_shifts_backbone(
            fsuv["cs_settings"]["cs_correction_res_ref"]
            )
    
    elif resonance_type=='Sidechains':
        exp.correct_shifts_sidechains()
    
    else:
        logs(
            'Choose a valid <resonance_type> argument.',
            fsuv["general_settings"]["logfile_name"]
            )
    
    return

def fill_na(peak_status, merit=0, details='None'):
    """
    A dictionary that configures how the fields of the added rows for 
    missing residues are fill.
    
    Parameters:
        peak_status (str): {'missing', 'unassigned'},
            how to fill 'Peak Status' column.
        
        merit (int/str): how to fill the 'Merit' column.
        
        details (str): how to fill the details column.
        
    Return:
        Dictionary of kwargs.
    """
    
    if not(peak_status in ['missing', 'unassigned']):
        input(
            'Choose a valid <peak_status> argument. Press Enter to continue.'
            )
        return None
    
    d = {
        'Peak Status': peak_status,
        'Merit': merit,
        'Details': details
        }
    
    return d

def expand_missing(exp, resonance_type='Backbone', dim='z'):
    """
    Checks for 'missing' residues accross the reference experiments
    for Y and Z axes.
    
    Uses FarseerCube.finds_missing().
    
    Compares reference peaklists along Y and Z axis of the Farseer-NMR
    Cube and generates the corresponding 'missing' residues.
    This function is useful when analysing dia/ and paramagnetic/ series
    along the Z axis.
    
    Parameters:
        exp (FarseerCube class instance): contains all peaklist data.
        
        dim (str): {'y', 'z'}, defaults to 'z'.
            The dimension along which references will be compared.
        
        resonance_type (str): {'Backbone', 'Sidechains'}, defaults to 
            'Backbone'.
    """
    
    if not(dim in ['y', 'z']):
        input('Choose a valid <dim> argument. Press Enter to continue.')
        return
    
    exp.compares_references(
        fill_na('missing'),
        along_axis=dim,
        resonance_type=resonance_type
        )
    
    return

def add_missing(exp, peak_status='missing', resonance_type='Backbone'):
    """
    Expands a <target> peaklist to the index of a <reference> peaklist.
    Uses FarseerCube.finds_missing().
    
    Parameters:
        exp (FarseerCube class instance): contains all peaklist data.
        
        peak_status (str): {'missing', 'unassigned'}, defaults to 'missing'.
            Peak status for the new generated entries for missing peaks. 
        
        resonance_type (str): {'Backbone', 'Sidechains'}, defaults to 
            'Backbone'.
    """
    
    if not(peak_status in ['missing', 'unassigned']):
        input(
            'Choose a valid <peak_status> argument. Press Enter to continue.'
            )
        return
    
    if not(resonance_type in ['Backbone', 'Sidechains']):
        input(
            'Choose a valid <resonance_type> argument. Press Enter to continue.'
            )
        return
    
    exp.finds_missing(
        fill_na(peak_status),
        missing=peak_status,
        resonance_type=resonance_type
        )
    
    return

def organize_columns(exp, fsuv, resonance_type='Backbone'):
    """
    Uses FarseerSet.organize_cols().
    
    Parameters:
        exp (FarseerCube class instance): contains all peaklist data.
        
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
        
        resonance_type (str): {'Backbone','Sidechains'}, defaults to 
            'Backbone'.
    
    Depends on:
    fsuv.perform_cs_correction
    """
    
    if not(resonance_type in ['Backbone', 'Sidechains']):
        input(
            'Choose a valid <resonance_type> argument. Press Enter to continue.'
            )
        return
    
    exp.organize_cols(
        performed_cs_correction=fsuv["cs_settings"]["perform_cs_correction"],
        resonance_type=resonance_type
        )
    
    return

def init_fs_cube(exp, fsuv):
    """
    Inits Farseer-NMR Cube.
    The Cube is stored as an attribute of the FarseerCube instance.
    
    Parameters:
        exp (FarseerCube class instance): contains all peaklist data.
        
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
    
    Depends on:
    fsuv.use_sidechains
    """
    
    exp.init_Farseer_cube(
        use_sidechains=fsuv["general_settings"]["use_sidechains"]
        )
    
    return

def series_kwargs(fsuv, resonance_type='Backbone'):
    """
    Defines the kwargs dictionary that will be used to generate
    the FarseerSeries object based on the user defined preferences.
    
    Parameters:
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
        
        resonance_type (str): {'Backbone', 'Sidechains'}, whether data 
            corresponds to one or another.
    
    Depends on:
    fsuv.csp_alpha4res
    fsuv.csp_res_exceptions
    fsuv.cs_missing
    fsuv.restraint_names
    """
    
    if not(resonance_type in ['Backbone', 'Sidechains']):
        input(
            'Choose a valid <resonance_type> argument. Press Enter to continue.'
            )
        return None
    
    dd = {
        'resonance_type':resonance_type,
        'csp_alpha4res':fsuv["csp_settings"]["csp_res4alpha"],
        'csp_res_exceptions':fsuv["csp_settings"]["csp_res_exceptions"],
        'cs_missing':fsuv["csp_settings"]["cs_missing"],
        'restraint_list':fsuv["restraint_names"],
        'log_export_onthefly':True,
        'log_export_name':fsuv["general_settings"]["logfile_name"]
        }
    
    return dd

def gen_series_dcts(exp, series_class, fsuv, resonance_type='Backbone'):
    """
    Generates a nested dictionary, <D>, containing all possible series
    over all the three Farseer-NMR Cube axis.
    
    Parameters:
        exp (FarseerCube class instance): contains all peaklist data.
        
        series_class (FarseerSeries class): The class that will 
            initiate the series, normally fslibs/FarseerSeries.py
        
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
        
        resonance_type OPT (stg): {'Backbone', 'Sidechains'} depending
            on data in <exp>.
    
    
    <D> contains a first level key for each Farseer-NMR Cube's axis.
    Each of these keys contains a second nested dictionary enclosing
    all the experimental series along that axis as extracted from
    the Farseer-NMR Cube.
    
    Creates series only for user activated axis.
    
    The first level keys of the experimental series are the "next axis"
    datapoints, second level keys are the "previous axis" datapoints.
    
    Example:
        for X axis series, keys are:
            Y1
                Z1
                Z2
            Y2
                Z1
                Z2
        
        for Z axis series:
            X1
                Y1
                Y2
            X2
                Y1
                Y2
    
    Depends on:
    fsuv.do_along_x
    fsuv.do_along_y
    fsuv.do_along_z
    """
    
    if not(resonance_type in ['Backbone', 'Sidechains']):
        input(
            'Choose a valid <resonance_type> argument. Press Enter to continue.'
            )
        return None
    
    if not(_checks_cube_axes_flags()):
        return None
    
    series_dct = {}
    xx = False
    yy = False
    zz = False
    
    # creates set of series for the first condition (1D)
    if exp.hasxx and fsuv["fitting_settings"]["do_along_x"]:
        xx = True
        series_dct['along_x'] = \
            exp.export_series_dict_over_axis(
                series_class,
                along_axis='x',
                resonance_type=resonance_type,
                series_kwargs=\
                    series_kwargs(fsuv, resonance_type=resonance_type)
                )
    
    elif not(exp.hasxx) and fsuv["fitting_settings"]["do_along_x"]:
        checks_axis_coherency('x', fsuv)
    
    # creates set of series for the second condition (2D)
    if exp.hasyy and fsuv["fitting_settings"]["do_along_y"]:
        yy = True
        series_dct['along_y'] = \
            exp.export_series_dict_over_axis(
                series_class,
                along_axis='y',
                resonance_type=resonance_type,
                series_kwargs=\
                    series_kwargs(fsuv, resonance_type=resonance_type)
                )
    
    elif not(exp.hasyy) and fsuv["fitting_settings"]["do_along_y"]:
        checks_axis_coherency('y', fsuv)

    # creates set of series for the third condition (3D)  
    if exp.haszz and fsuv["fitting_settings"]["do_along_z"]:
        zz = True
        series_dct['along_z'] = \
            exp.export_series_dict_over_axis(
                series_class,
                along_axis='z',
                resonance_type=resonance_type,
                series_kwargs=\
                    series_kwargs(fsuv, resonance_type=resonance_type)
                )
    
    elif not(exp.haszz) and fsuv["fitting_settings"]["do_along_z"]:
        checks_axis_coherency('z', fsuv)
    
    if not(any([xx, yy, zz])):
        msg = \
'The overall combination of data and calculation flags is not consistent and \
any series set was created along an axis. Nothing will be calculated.'
        wet20 = fsw(msg_title='WARNING', msg=msg, wet_num=20)
        logs(wet20.wet, fsuv["general_settings"]["logfile_name"])
    
    return series_dct

def eval_series(series_dct, fsuv, resonance_type='Backbone'):
    """
    Executes the Farseer-NMR Analysis Routines over all the series of
    the activated Farseer-NMR Cube Axes.
    
    Parameters:
        series_dct (dict): a nested dictionary containing the
            FarseerSeries for every axis of the Farseer-NMR Cube.
        
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
    
        resonance_type OPT (str): {'Backbone', 'Sidechains'}
            whether the data in <series_dct> corresponds to backbone or
            sidechain resonances.
    """
    
    if not(resonance_type in ['Backbone', 'Sidechains']):
        input(
           'Choose a valid <resonance_type> argument. Press Enter to continue.'
            )
        return
    
    # for each kind of titration (cond{1,2,3})
    for cond in sorted(series_dct.keys()):
        # for each point in the corresponding second dimension/condition
        for dim2_pt in sorted(series_dct[cond].keys()):
            # for each point in the corresponding first dimension/condition
            for dim1_pt in sorted(series_dct[cond][dim2_pt].keys()):
                series_dct[cond][dim2_pt][dim1_pt].\
                    log_r(
                        'ANALYZING... [{}] - [{}][{}]'.format(
                            cond,
                            dim2_pt,
                            dim1_pt
                            ),
                        istitle=True)
                # flags and checks are under each function.
                # performs the calculations
                perform_calcs(series_dct[cond][dim2_pt][dim1_pt], fsuv)
                # PERFORMS FITS
                perform_fits(series_dct[cond][dim2_pt][dim1_pt], fsuv)
                # Analysis of PRE data - only in along_z
                PRE_analysis(series_dct[cond][dim2_pt][dim1_pt], fsuv)
                # EXPORTS FULLY PARSED PEAKLISTS
                exports_series(series_dct[cond][dim2_pt][dim1_pt])
                # EXPORTS CHIMERA FILES
                exports_chimera_att_files(\
                    series_dct[cond][dim2_pt][dim1_pt], fsuv)
                exports_all_parameters(
                    series_dct[cond][dim2_pt][dim1_pt],
                    fsuv,
                    resonance_type=resonance_type
                    )
                # PLOTS DATA
                # plots data are exported together with the plots in
                # fsT.plot_base(), but can be used separatly with
                # fsT.write_table()
                plots_data(
                    series_dct[cond][dim2_pt][dim1_pt],
                    fsuv,
                    resonance_type=resonance_type
                    )
    
    return

def perform_calcs(farseer_series, fsuv):
    """
    Calculates the NMR restraints according to the user specifications.
    
    Parameters:
        farseer_series (FarseerSeries class): a FarseerSeries class
            object containing all the experiments along a series
            previously selected from the Farseer-NMR Cube.
        
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
    
    Depends on:
    fsuv["PosF1_settings"]["calcs_PosF1_delta"]
    fsuv["PosF2_settings"]["calcs_PosF2_delta"]
    fsuv.calcs_CSP
    fsuv["Height_ratio_settings"]["calcs_Height_ratio"]
    fsuv["Volume_ratio_settings"]["calcs_Volume_ratio"]
    fsuv.calccol_name_PosF1_delta
    fsuv.calccol_name_PosF2_delta
    fsuv.calccol_name_CSP
    fsuv.calccol_name_Height_ratio
    fsuv.calccol_name_Volume_ratio
    """
    
    checks_calculation_flags(fsuv)
    
    # if the user wants to calculate combined Chemical Shift Perturbations
    if fsuv["csp_settings"]["calcs_CSP"]:
        # calculate differences in chemical shift for each dimension
        farseer_series.calc_cs_diffs(
            fsuv["PosF1_settings"]["calccol_name_PosF1_delta"],
            'Position F1'
            )
        farseer_series.calc_cs_diffs(
            fsuv["PosF2_settings"]["calccol_name_PosF2_delta"],
            'Position F2'
            )
        # Calculates CSPs
        farseer_series.calc_csp(
            calccol=fsuv["csp_settings"]["calccol_name_CSP"],
            pos1=fsuv["PosF1_settings"]["calccol_name_PosF1_delta"],
            pos2=fsuv["PosF2_settings"]["calccol_name_PosF2_delta"]
            )
    
    # if the user only wants to calculate perturbation in single dimensions
    else:
        if fsuv["PosF1_settings"]["calcs_PosF1_delta"]:
            farseer_series.calc_cs_diffs(
                fsuv["PosF1_settings"]["calccol_name_PosF1_delta"],
                'Position F1'
                )
        if fsuv["PosF2_settings"]["calcs_PosF2_delta"]:
            farseer_series.calc_cs_diffs(
                fsuv["PosF2_settings"]["calccol_name_PosF2_delta"],
                'Position F2'
                )
    
    # Calculates Ratios
    if fsuv["Height_ratio_settings"]["calcs_Height_ratio"]:
        farseer_series.calc_ratio(
            fsuv["Height_ratio_settings"]["calccol_name_Height_ratio"],
            'Height'
            )
    
    if fsuv["Volume_ratio_settings"]["calcs_Volume_ratio"]:
        farseer_series.calc_ratio(
            fsuv["Volume_ratio_settings"]["calccol_name_Volume_ratio"],
            'Volume'
            )
    
    ### ADD ADDITIONAL CALCULATION HERE ###
    
    return

def perform_fits(farseer_series, fsuv): 
    """
    Performs fits for 1H, 15N and CSPs data along the X axis series.
    
    Parameters:
        farseer_series (FarseerSeries class): a FarseerSeries class
            object containing all the experiments along a series
            previously selected from the Farseer-NMR Cube.
        
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
    
    Depends on:
    fsuv.perform_resevo_fit
    fsuv.restraint_settings
    fsuv["revo_settings"]["titration_x_values"]
    fsuv["fitting_parameters"]
    """
    # fits are allowed only for X axis series
    if not(
            fsuv["revo_settings"]["perform_resevo_fitting"] \
                and farseer_series.series_axis == 'along_x'
            ):
        return
    
    checks_fit_input(farseer_series, fsuv)
    
    for restraint in fsuv["restraint_settings"].index:
        if fsuv["restraint_settings"].loc[restraint, 'calcs_restraint_flg']:
            farseer_series.perform_fit(
                restraint,
                fsuv["revo_settings"]["titration_x_values"],
                fsuv["fitting_parameters"]["mininum_datapoints"],
                fsuv["fitting_parameters"]["fitting_function"]
                )
    
    for obs in fsuv["observables_settings"].index:
        if fsuv["observables_settings"].loc[obs, 'obs_flags']:
            farseer_series.perform_fit(
                obs,
                fsuv["revo_settings"]["titration_x_values"],
                fsuv["fitting_parameters"]["mininum_datapoints"],
                fsuv["fitting_parameters"]["fitting_function"]
                )
    
    return

def PRE_analysis(farseer_series, fsuv):
    """
    Optimized algorythm that performs all possible PRE analysis.
    
    Parameters:
        farseer_series (FarseerSeries class): a FarseerSeries class
            object containing all the experiments along a series
            previously selected from the Farseer-NMR Cube.
        
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
    
    Depends on:
    fsuv.apply_PRE_analysis
    fsuv.restraint_settings
    fsuv.gaussian_stddev
    fsuv.gauss_x_size
    fsuv.restraint_settings
    fsuv.heat_map_rows
    fsuv.fig_height
    fsuv.fig_width
    fsuv.DPRE_plot_width
    fsuv.fig_file_type
    fsuv.fig_dpi
    """
    
    # if user do not wants PRE analysis, do nothing
    if not(fsuv["pre_settings"]["apply_PRE_analysis"]):
        return
    
    isalong_z = farseer_series.series_axis == 'along_z'
    iscz = farseer_series.series_axis == 'Cz'
    isprev_para = farseer_series.prev_dim in farseer_series.paramagnetic_names
    isnext_para = farseer_series.next_dim in farseer_series.paramagnetic_names
    do_heatmap = fsuv['plotting_flags']['do_heat_map']
    
    # if analysing along_z: performs calculations.
    if isalong_z:
        farseer_series.load_theoretical_PRE(
            fsuv["general_settings"]["input_spectra_path"],
            farseer_series.prev_dim
            )
        
        for sourcecol, targetcol in zip(
                fsuv["restraint_settings"].index[3:],
                ['Hgt_DPRE', 'Vol_DPRE']
                ):
            # only in the parameters allowed by the user
            if fsuv["restraint_settings"].loc[sourcecol,'calcs_restraint_flg']:
                farseer_series.calc_Delta_PRE(
                    sourcecol,
                    targetcol,
                    gaussian_stddev=fsuv["pre_settings"]["gaussian_stdev"],
                    guass_x_size=fsuv["pre_settings"]["gauss_x_size"]
                    )
    
    # plots the calculated Delta_PRE and Delta_PRE_smoothed analsysis
    # for along_z and for comparison Cz.
    if (isalong_z or (iscz and (isprev_para or isnext_para))) and do_heatmap:
        for sourcecol, targetcol in zip(
                list(fsuv["restraint_settings"].index[3:])*2,
                ['Hgt_DPRE','Vol_DPRE','Hgt_DPRE_smooth','Vol_DPRE_smooth']
                ):
            # only for the parameters allowed by the user
            if fsuv["restraint_settings"].loc[sourcecol,'calcs_restraint_flg']:
                farseer_series.plot_base(
                    targetcol, 
                    'exp', 
                    'heat_map',
                    fsuv["heat_map_settings"],
                    par_ylims=\
                        fsuv["restraint_settings"].\
                            loc[sourcecol,'plt_y_axis_scl'],
                    ylabel=\
                        fsuv["restraint_settings"].\
                            loc[sourcecol,'plt_y_axis_lbl'],
                    cols_per_page=1,
                    rows_per_page=\
                        fsuv["heat_map_settings"]["rows"],
                    fig_height=fsuv["general_settings"]["fig_height"],
                    fig_width=fsuv["general_settings"]["fig_width"],
                    fig_file_type=fsuv["general_settings"]["fig_file_type"],
                    fig_dpi=fsuv["general_settings"]["fig_dpi"]
                    )
    
    # plots the DeltaPRE analysis only for <Cz> comparison.
    # because DeltaPRE represents the results obtained only
    # for paramagnetic data.
    if (iscz and (isprev_para or isnext_para)) \
            and fsuv['plotting_flags']['do_DPRE_plot']:
        for sourcecol, targetcols in zip(
                fsuv["restraint_settings"].index[3:],
                ['Hgt_DPRE', 'Vol_DPRE']
                ):
            if fsuv["restraint_settings"].loc[sourcecol,'calcs_restraint_flg']:
                farseer_series.plot_base(
                    targetcols,
                    'exp',
                    'DPRE_plot',
                    {
                        **fsuv["series_plot_settings"], 
                        **fsuv["DPRE_plot_settings"]
                        },
                    cols_per_page=1,
                    rows_per_page=fsuv["DPRE_plot_settings"]["rows"],
                    fig_height=fsuv["general_settings"]["fig_height"],
                    fig_width=\
                        fsuv["general_settings"]["fig_width"]/\
                        fsuv["DPRE_plot_settings"]["width"],
                    fig_file_type=fsuv["general_settings"]["fig_file_type"],
                    fig_dpi=fsuv["general_settings"]["fig_dpi"])
    
    return

def exports_series(farseer_series):
    """
    Exports FarseerSeries to tsv files.
    
    Uses FarseerSeries.export_seres_to_tsv()
    
    Parameters:
        farseer_series (FarseerSeries instance)
    """
    
    farseer_series.export_series_to_tsv()
    
    return

def exports_chimera_att_files(farseer_series, fsuv):
    """
    Exports formatted UCSF Chimera Attribute files for the
    calculated restraints.
    
    http://www.cgl.ucsf.edu/chimera/docs/ContributedSoftware/defineattrib/defineattrib.html#attrfile
    
    Parameters:
        farseer_series (FarseerSeries instance): contains all the
            experiments of a Farseer-NMR Cube extracted series.
        
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
    
    Depends on:
    fsuv.restraint_settings
    fsuv.chimera_att_select_format
    """
    
    for restraint in fsuv["restraint_settings"].index:
        # if the user wants to plot this parameter
        if fsuv["restraint_settings"].loc[restraint,'calcs_restraint_flg']:
            # do export chimera attribute files
            farseer_series.write_Chimera_attributes(
                    restraint,
                    resformat=\
                        fsuv["general_settings"]["chimera_att_select_format"]
                    )
    
    return

def exports_all_parameters(farseer_series, fsuv, resonance_type='Backbone'):
    """
    Exports the evolution of all parameters in separated tables.
    
    Table rows are residues and columns are series datapoints.
    """
    
    if not(resonance_type in ['Backbone', 'Sidechains']):
        input(
            'Choose a valid <resonance_type> argument. Press Enter to continue.'
            )
        return
    
    # Exports calculated parameters
    for restraint in fsuv["restraint_settings"].index:
        if fsuv["restraint_settings"].loc[restraint,'calcs_restraint_flg']:
            farseer_series.write_table(
                restraint,
                restraint,
                resonance_type=resonance_type
                )
    
    # Exports all observables and user annotations
    list_of_observables = [
        "Peak Status",
        "Position F2",
        "Position F1",
        "Height",
        "Volume",
        "Line Width F1 (Hz)",
        "Line Width F2 (Hz)",
        "Merit",
        "Details",
        "Fit Method",
        "Vol. Method"
        ]
    
    for observable in list_of_observables:
        farseer_series.write_table(
            "observables/"+observable,
            observable,
            resonance_type=resonance_type
            )
    
    return

def plots_data(farseer_series, fsuv, resonance_type='Backbone'):
    """
    Walks through the plotting routines and plots according to user
    preferences.
    
    Parameters:
        farseer_series (FarseerSeries class): contains all the
            experiments of a Farseer-NMR Cube extracted series.
        
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
    
    Depends on:
    fsuv["plotting_flags"]["do_ext_bar"]
    fsuv["plotting_flags"]["do_comp_bar"]
    fsuv["plotting_flags"]["do_vert_bar"]
    fsuv["plotting_flags"]["do_res_evo"]
    fsuv["plotting_flags"]["do_cs_scatter"]
    fsuv["plotting_flags"]["do_cs_scatter_flower"]
    fsuv.restraint_settings
    fsuv["series_plot_settings"]
    fsuv["bar_plot_settings"]
    fsuv["extended_bar_settings"]
    fsuv["compact_bar_settings"]
    fsuv["revo_settings"]
    fsuv.res_evo_par_dict
    fsuv.cs_scatter_par_dict
    fsuv.cs_scatter_flower_dict
    """
    
    if not(resonance_type in ['Backbone', 'Sidechains']):
        input(
            'Choose a valid <resonance_type> argument. Press Enter to continue.'
            )
        return
    
    are_plots = checks_plotting_flags(farseer_series, fsuv, resonance_type)
    
    if not(are_plots):
        return
    
    fig_height = fsuv["general_settings"]["fig_height"]
    fig_width = fsuv["general_settings"]["fig_width"]
    fig_dpi = fsuv["general_settings"]["fig_dpi"]
    fig_file_type = fsuv["general_settings"]["fig_file_type"]
    
    for restraint in fsuv["restraint_settings"].index:
        # if the user has calculated this restraint
        if fsuv["restraint_settings"].loc[restraint,'calcs_restraint_flg']:
            if farseer_series.resonance_type == 'Backbone':
                # Plot Extended Bar Plot
                if fsuv["plotting_flags"]["do_ext_bar"]:
                    farseer_series.plot_base(
                        restraint,
                        'exp',
                        'bar_extended',
                        {
                            **fsuv["series_plot_settings"],
                            **fsuv["bar_plot_settings"],
                            **fsuv["extended_bar_settings"]
                            },
                        par_ylims=\
                            fsuv["restraint_settings"].\
                                loc[restraint,'plt_y_axis_scl'],
                        ylabel=\
                            fsuv["restraint_settings"].\
                                loc[restraint,'plt_y_axis_lbl'],
                        hspace=fsuv["series_plot_settings"]["vspace"],
                        cols_per_page=\
                            fsuv["extended_bar_settings"]["cols_page"],
                        rows_per_page=\
                            fsuv["extended_bar_settings"]["rows_page"],
                        fig_height=fig_height,
                        fig_width=fig_width,
                        fig_file_type=fig_file_type,
                        fig_dpi=fig_dpi
                        )
                
                # Plot Compacted Bar Plot
                if fsuv["plotting_flags"]["do_comp_bar"]:
                    farseer_series.plot_base(\
                        restraint,
                        'exp',
                        'bar_compacted',
                        {
                            **fsuv["series_plot_settings"],
                            **fsuv["bar_plot_settings"],
                            **fsuv["compact_bar_settings"]
                            },
                        par_ylims=\
                            fsuv["restraint_settings"].\
                                loc[restraint,'plt_y_axis_scl'],
                        ylabel=\
                            fsuv["restraint_settings"].\
                                loc[restraint,'plt_y_axis_lbl'],
                        hspace=fsuv["series_plot_settings"]["vspace"],
                        cols_per_page=\
                            fsuv["compact_bar_settings"]["cols_page"],
                        rows_per_page=\
                            fsuv["compact_bar_settings"]["rows_page"],
                        fig_height=fig_height,
                        fig_width=fig_width,
                        fig_file_type=fig_file_type,
                        fig_dpi=fig_dpi
                        )
            
                # Plot Vertical Bar Plot
                if fsuv["plotting_flags"]["do_vert_bar"]:
                    farseer_series.plot_base(
                        restraint,
                        'exp',
                        'bar_vertical',
                        {
                            **fsuv["series_plot_settings"],
                            **fsuv["bar_plot_settings"],
                            **fsuv["extended_bar_settings"]
                            },
                        par_ylims=\
                            fsuv["restraint_settings"].\
                                loc[restraint,'plt_y_axis_scl'],
                        ylabel=\
                            fsuv["restraint_settings"].\
                                loc[restraint,'plt_y_axis_lbl'],
                        cols_per_page=fsuv["vert_bar_settings"]["cols_page"],
                        rows_per_page=fsuv["vert_bar_settings"]["rows_page"],
                        fig_height=fig_height,
                        fig_width=fig_width,
                        fig_file_type=fig_file_type,
                        fig_dpi=fig_dpi
                        )
            
            # Sidechain data is represented in a different bar plot
            elif farseer_series.resonance_type == 'Sidechains'\
                    and (fsuv["plotting_flags"]["do_ext_bar"] \
                    or fsuv["plotting_flags"]["do_comp_bar"]):
                farseer_series.plot_base(
                    restraint,
                    'exp',
                    'bar_extended',
                    {
                        **fsuv["series_plot_settings"],
                        **fsuv["bar_plot_settings"],
                        **fsuv["extended_bar_settings"]
                        },
                    par_ylims=\
                        fsuv["restraint_settings"].\
                            loc[restraint,'plt_y_axis_scl'],
                    ylabel=\
                        fsuv["restraint_settings"].\
                            loc[restraint,'plt_y_axis_lbl'],
                    hspace=fsuv["series_plot_settings"]["vspace"],
                    cols_per_page=fsuv["extended_bar_settings"]["cols_page"],
                    rows_per_page=fsuv["extended_bar_settings"]["rows_page"],
                    resonance_type='Sidechains',
                    fig_height=fig_height,
                    fig_width=fig_width/2,
                    fig_file_type=fig_file_type,
                    fig_dpi=fig_dpi
                    )
            
            # Plots Parameter Evolution Plot
            if fsuv["plotting_flags"]["do_res_evo"]:
                farseer_series.plot_base(
                    restraint,
                    'res',
                    'res_evo',
                    {**fsuv["revo_settings"], **fsuv["res_evo_settings"]},
                    par_ylims=\
                        fsuv["restraint_settings"].\
                            loc[restraint,'plt_y_axis_scl'],
                    ylabel=\
                        fsuv["restraint_settings"].\
                            loc[restraint,'plt_y_axis_lbl'],
                    cols_per_page=fsuv["res_evo_settings"]["cols_page"],
                    rows_per_page=fsuv["res_evo_settings"]["rows_page"],
                    fig_height=fig_height,
                    fig_width=fig_width,
                    fig_file_type=fig_file_type,
                    fig_dpi=fig_dpi
                    )
    
    if fsuv["plotting_flags"]["do_cs_scatter"] \
            and ((fsuv["PosF1_settings"]["calcs_PosF1_delta"] \
                and fsuv["PosF2_settings"]["calcs_PosF2_delta"])\
            or fsuv["csp_settings"]["calcs_CSP"]):
        farseer_series.plot_base(
            '15N_vs_1H',
            'res',
            'cs_scatter',
            {**fsuv["revo_settings"], **fsuv["cs_scatter_settings"]},
            cols_per_page=fsuv["cs_scatter_settings"]["cols_page"],
            rows_per_page=fsuv["cs_scatter_settings"]["rows_page"],
            fig_height=fig_height,
            fig_width=fig_width,
            fig_file_type=fig_file_type,
            fig_dpi=fig_dpi
            )
    
    if fsuv["plotting_flags"]["do_cs_scatter_flower"] \
            and ((fsuv["PosF1_settings"]["calcs_PosF1_delta"] \
                and fsuv["PosF2_settings"]["calcs_PosF2_delta"])\
            or fsuv["csp_settings"]["calcs_CSP"]):
        farseer_series.plot_base(
            '15N_vs_1H',
            'single',
            'cs_scatter_flower',
            {**fsuv["revo_settings"], **fsuv["cs_scatter_flower_settings"]},
            cols_per_page=2,
            rows_per_page=3,
            fig_height=fig_height,
            fig_width=fig_width,
            fig_file_type=fig_file_type,
            fig_dpi=fig_dpi
            )
    
    for obs in fsuv["observables_settings"].index:
        if fsuv["observables_settings"].loc[obs,"obs_flags"]:
            farseer_series.plot_base(
            obs,
            'res',
            'res_evo',
            {**fsuv["revo_settings"], **fsuv["res_evo_settings"]},
            par_ylims=fsuv["observables_settings"].loc[obs,"obs_yaxis_scl"],
            ylabel=fsuv["observables_settings"].loc[obs,"obs_yaxis_lbl"],
            cols_per_page=fsuv["res_evo_settings"]["cols_page"],
            rows_per_page=fsuv["res_evo_settings"]["rows_page"],
            fig_height=fig_height,
            fig_width=fig_width,
            fig_file_type=fig_file_type,
            fig_dpi=fig_dpi
            )
    
    return

def comparison_analysis_routines(comp_panel, fsuv, resonance_type):
    """
    The set of routines that are run for each comparative series.
    
    Parameters:
        comp_panel (FarseerSeries instance generated from 
            Comparisons.gen_next_dim or gen_prev_dim): contains all the 
            experiments parsed along an axis and for a specific
            Farseer-NMR Cube's coordinates.
        
        fsuv (module): contains user defined variables (preferences) after
        .read_user_variables().
        
        resonance_type (str): {'Backbone', 'Sidechains'}, depending on
            data type. Detaults to 'Backbone'.
    """
    
    if not(resonance_type in ['Backbone', 'Sidechains']):
        input(
            'Choose a valid <resonance_type> argument. Press Enter to continue.'
            )
        return
    
    # EXPORTS FULLY PARSED PEAKLISTS
    exports_series(comp_panel)
    # performs pre analysis
    PRE_analysis(comp_panel, fsuv)
    exports_chimera_att_files(comp_panel, fsuv)
    # plots data
    plots_data(comp_panel, fsuv, resonance_type=resonance_type)
    # writes parameters to tables
    exports_all_parameters(comp_panel, fsuv, resonance_type=resonance_type)
    
    return

def analyse_comparisons(series_dct, fsuv, resonance_type='Backbone'):
    """
    Algorythm to perform data comparisons over analysed conditions.
    
    Parameters:
        series_dct (dict): a nested dictionary containing the   
            FarseerSeries for every axis of the Farseer-NMR Cube.
        
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
    
    Returns:
        comp_dct (dict): a dictionary containing all the comparison
            objects created.
    """
    
    if not(resonance_type in ['Backbone', 'Sidechains']):
        input(
            'Choose a valid <resonance_type> argument. Press Enter to continue.'
            )
        return None
    
    # kwargs passed to the parsed series of class fss.FarseerSeries
    comp_kwargs = series_kwargs(fsuv, resonance_type=resonance_type)
    # ORDERED relation between dimension names
    # self: [next, prev]
    series_dim_keys = {
        'along_x':['along_y','along_z'],
        'along_y':['along_z','along_x'],
        'along_z':['along_x','along_y']
        }
    # stores all the comparison variables.
    comp_dct = {}
    
    # creates a Comparison object for each dimension that was evaluated
    # previously with fsuv.do_along_x, fsuv.do_along_y, fsuv.do_along_z
    for dimension in sorted(series_dct.keys()):
        # sends, along_x, along_y and along_z.
        # creates comparison
        c = fsc.Comparisons(
            series_dct[dimension].copy(),
            selfdim=dimension,
            other_dim_keys=series_dim_keys[dimension]
            )
        c.log_export_onthefly = True
        c.log_export_name = fsuv["general_settings"]["logfile_name"]
        # stores comparison in a dictionary
        comp_dct.setdefault(dimension, c)
        # generates set of PARSED FarseerSeries along the
        # next and previous dimensions
        c.gen_next_dim(fss.FarseerSeries, comp_kwargs)
        
        if c.has_points_next_dim:
            for dp2 in sorted(c.all_next_dim.keys()):
                for dp1 in sorted(c.all_next_dim[dp2].keys()):
                    if fsuv["pre_settings"]["apply_PRE_analysis"]:
                        c.all_next_dim[dp2][dp1].PRE_loaded = True
                    
                    # writes log
                    c.all_next_dim[dp2][dp1].log_r(
                        'COMPARING... [{}][{}][{}] - [{}]'.\
                            format(
                                dimension,
                                dp2,
                                dp1,
                                list(c.hyper_panel.labels)
                                ),
                        istitle=True
                        )
                    # performs ploting routines
                    comparison_analysis_routines(
                        c.all_next_dim[dp2][dp1],
                        fsuv,
                        resonance_type
                        )
        
        c.gen_prev_dim(fss.FarseerSeries, comp_kwargs)
        
        if c.has_points_prev_dim:
            for dp2 in sorted(c.all_prev_dim.keys()):
                for dp1 in sorted(c.all_prev_dim[dp2].keys()):
                    if fsuv["pre_settings"]["apply_PRE_analysis"]:
                        c.all_prev_dim[dp2][dp1].PRE_loaded = True
                    
                    # writes log
                    c.all_prev_dim[dp2][dp1].log_r(
                        'COMPARING... [{}][{}][{}] - [{}]'.\
                            format(
                                dimension,
                                dp2,
                                dp1,
                                list(c.hyper_panel.cool)
                                ),
                        istitle=True)
                    comparison_analysis_routines(
                        c.all_prev_dim[dp2][dp1],
                        fsuv,
                        resonance_type
                        )
    
    return comp_dct

def run_farseer(fsuv, logger=None):
    """
    Runs the whole Farseer-NMR standard algorithm.
    
    Parameters:
        fsuv (module): contains user defined variables (preferences)
            after .read_user_variables().
    """
    logger = logger or start_logger(fsuv["general_settings"]["output_path"])
    
    general = fsuv["general_settings"]
    fitting = fsuv["fitting_settings"]
    cs = fsuv["cs_settings"]
    csp = fsuv["csp_settings"]
    fasta = fsuv["fasta_settings"]
    use_sidechains = general["use_sidechains"]
    # Initiates the log
    log_init(fsuv)
    # performs initial checks
    initial_checks(fsuv)
    # Initiates Farseer
    exp = creates_farseer_dataset(fsuv)
    # reads input
    reads_peaklists(exp, fsuv)
    #inits_coords_names(exp)
    # identify residues
    identify_residues(exp)
    
    # corrects chemical shifts
    if cs["perform_cs_correction"]:
        correct_shifts(exp, fsuv, resonance_type='Backbone')
        
        if exp.has_sidechains and use_sidechains:
            correct_shifts(exp, fsuv, resonance_type='Sidechains')
    
    # expands missing residues to other dimensions
    if fitting["expand_missing_yy"]:
        expand_missing(exp, dim='y')
        
        if exp.has_sidechains and use_sidechains:
            expand_missing(exp, dim='y', resonance_type='Sidechains')
    
    if fitting["expand_missing_zz"]:
        expand_missing(exp, dim='z')
        
        if exp.has_sidechains and use_sidechains:
            expand_missing(exp, dim='z', resonance_type='Sidechains')
    
    ## identifies missing residues
    add_missing(exp, peak_status='missing')
    
    if exp.has_sidechains and use_sidechains:
        add_missing(exp, peak_status='missing', resonance_type='Sidechains')
    
    # adds fasta
    if fasta["applyFASTA"]:
        add_missing(exp, peak_status='unassigned')
    
    #organize peaklist columns
    organize_columns(exp, fsuv)
    
    if exp.has_sidechains and use_sidechains:
        organize_columns(exp, fsuv, resonance_type='Sidechains')
    
    init_fs_cube(exp, fsuv)
    # initiates a dictionary that contains all the series to be evaluated
    # along all the conditions.
    farseer_series_dct = \
        gen_series_dcts(
            exp,
            fss.FarseerSeries,
            fsuv,
            resonance_type='Backbone'
            )
    
    if not(farseer_series_dct):
        exp.exports_parsed_pkls()
    
    else:
        # evaluates the series and plots the data
        eval_series(farseer_series_dct, fsuv)
    
    if exp.has_sidechains and use_sidechains:
        farseer_series_SD_dict = \
            gen_series_dcts(
                exp,
                fss.FarseerSeries,
                fsuv,
                resonance_type='Sidechains'
                )
        
        if (farseer_series_SD_dict):
            eval_series(
                farseer_series_SD_dict,
                fsuv,
                resonance_type='Sidechains'
                )
    
    # Representing the results comparisons
    if fitting["perform_comparisons"] and (farseer_series_dct):
        # analyses comparisons.
        comparison_dict = \
            analyse_comparisons(
                farseer_series_dct,
                fsuv,
                resonance_type='Backbone'
                )
    
    if (fitting["perform_comparisons"] and farseer_series_dct) \
            and (exp.has_sidechains and use_sidechains):
        comparison_dict_SD = \
            analyse_comparisons(
                farseer_series_SD_dict,
                fsuv,
                resonance_type='Sidechains'
                )
    
    log_end(fsuv)
    
    return

if __name__ == '__main__':
    
    b = FarseerNMR(sys.argv[1])
    b.logger.debug('done reading from json path')
    
    #logger = start_logger(sys.argv[1])
    #fsuv = read_user_variables(sys.argv[1], sys.argv[2])
    fsuv = json.load(open(sys.argv[1], 'r'))
    a = FarseerNMR(fsuv)
    a.logger.debug('done reading from json dict')
    
    
    # copy_Farseer_version(fsuv)
    
    # path evaluations now consider the absolute path, always.
    # in this way the user can run farseer from any folder taking the
    # input from any other folder.
    # path should be the folder where the 'spectra/' are stored and NOT the
    # path to the 'spectra/' folder.
    
    #run_farseer(fsuv, logger=logger)
    #logger.debug('Farseermain.py finished with __name__ == "__main__"')
