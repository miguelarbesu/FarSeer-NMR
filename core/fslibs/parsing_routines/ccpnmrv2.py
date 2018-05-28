"""
Copyright © 2017-2018 Farseer-NMR
Teixeira, J.M.C., Skinner, S.P., Arbesú, M. et al. J Biomol NMR (2018).
https://doi.org/10.1007/s10858-018-0182-5

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
"""
def parse_ccpnmrv2_peaklist(peaklist_file):
    """
    Parses CCPNMRv2 peaklists into the peakList class format.
    
    Parameters:
        - peaklist_file: path to peaklist file.
    
    Returns peakList object
    """
    fin = pd.read_csv(peaklist_file)
    peakList = []
    atoms = []
    
    for row in fin.index:
        
        if fin.loc[row,'Assign F1'] in aal1tol3.values():
            atoms.append(fin.loc[row,'Assign F1'][-1])
        
        if fin.loc[row,'Assign F2'] in aal1tol3.values():
            atoms.append(fin.loc[row,'Assign F2'][-1])
        
        peak = Peak(
            peak_number=fin.loc[row,'Number'],
            positions=[
                fin.loc[row,'Position F1'],
                fin.loc[row,'Position F2']
                ],
            atoms=atoms,
            residue_number=fin.loc[row,'Assign F1'].str[:,-4],
            residue_type=fin.loc[row,'Assign F1'].str[-4,:],
            linewidths=[
                fin.loc[row,'Line Width F1 (Hz)'],
                fin.loc[row,'Line Width F2 (Hz)']
                ],
            volume=fin.loc[row,'Volume'],
            height=fin.loc[row,'Height'],
            fit_method=fin.loc[row,'Fit Method'],
            merit=fin.loc[row,'Merit'],
            volume_method=fin.loc[row,'Vol. Method'],
            details=fin.loc[row,'Details'],
            format='ccpnmrv2'
            )
        peakList.append(peak)
    
    return peakList
