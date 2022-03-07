# water X-ray attenuation/density coefficient: https://physics.nist.gov/PhysRefData/XrayMassCoef/ComTab/water.html
import argparse
import numpy as np
import xlrd
from scipy import interpolate
import prettytable as pt


class WaterAttenuationCoefficientReference:
    def __init__(self, path):
        self.spectrum_path = path
        self.attention_density_path = r'mass attenuation coefficient.xlsx'
        self.density = 1.0  # g/cm^3

    def read_attenuation_per_density(self):
        self.workbook = xlrd.open_workbook(self.attention_density_path)
        self.sheet = self.workbook.sheet_by_index(0)
        self.rows, self.cols = self.sheet.nrows, self.sheet.ncols

        # attenuation/density in 10、15、20、30、40、50、60、80、100、150 keV
        self.energy = self.sheet.col_values(1)[10:20]
        self.attenuation = np.array(self.sheet.col_values(2)[10:20]) * self.density

    def attenuation_interp(self):
        """
        Logarithmic interpolation of the attenuation coefficient of water
        """
        energy_log = np.log(self.energy)
        miu_log = np.log(self.attenuation)
        f_log = interpolate.interp1d(energy_log, miu_log, kind=1)
        energy_new = np.linspace(0.01, 0.14, 131)  # usually doesn't change, constant in the physical sense
        miu_new_log = np.exp(f_log(np.log(energy_new)))
        self.energy_new = energy_new  # 10-140 keV
        self.attenuation_new = miu_new_log

    def read_spectrum_file(self):
        spec_energy_range = []  # input spectrum energy range
        photons = []
        with open(self.spectrum_path, 'r') as f:
            for line in f.readlines():
                if not line.strip('\n'):  # end of the energy and photons line
                    break
                energy, photons_nums = line.strip('\n').split()
                spec_energy_range.append(energy)
                photons.append(photons_nums)

        spec_energy_range = np.array(spec_energy_range, dtype=np.int)
        spec_energy_range = spec_energy_range // 1000 \
            if spec_energy_range[0] > 1000 else spec_energy_range  # unify as keV, leave out MeV
        photons = np.array(photons, dtype=np.float)

        self.start_voltage = max(spec_energy_range[0], 10)  # start voltage is compared to interpolation's begin
        for i in range(len(photons)-1, -1, -1):  # find the cut-off voltage in reverse order
            if int(photons[i]) == -1:  # deal with '-1' end line
                continue
            if int(photons[i]) != 0:
                self.cutoff_voltage = spec_energy_range[i]
                break
        # adjust the spectrum range
        start = np.where(spec_energy_range == self.start_voltage)[0][0]
        end = np.where(spec_energy_range == self.cutoff_voltage)[0][0] + 1
        self.photons = np.array(photons[start: end], dtype=np.float)

    def calc_ref(self, detector='FPD'):
        assert (detector == 'FPD' or detector == 'PCD'), 'Only support FPD and PCD'
        # __init__
        self.read_attenuation_per_density()
        self.attenuation_interp()
        self.read_spectrum_file()
        # choose right attention/density range from 10-140 keV
        start = self.start_voltage - 10
        end = self.cutoff_voltage - 10 + 1
        energy_range = 1 if detector == 'PCD' else np.linspace(self.start_voltage, self.cutoff_voltage, end-start)
        miu_ref = sum(self.photons * energy_range * self.attenuation_new[start: end]) / sum(self.photons * energy_range) / 10
        # output to screen
        tb = pt.PrettyTable()
        tb.field_names = ['Start Voltage', 'Cut-off Voltage', 'μ_water,ref']
        tb.add_row([str(self.start_voltage)+' keV', str(self.cutoff_voltage+1)+' keV', str("%.5f" % miu_ref)+' mm^-1'])
        print(tb.get_string(title='Water Attenuation Coefficient Reference ({})'.format(detector)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('dir', nargs='+', help='Spectrum file path')
    parser.add_argument('-d', '--detector', default='FPD', help='FPD: flat panel detector,\n'
                                                                'PCD: photon counting detector\n'
                                                                'default is FPD')
    args = parser.parse_args()
    water = WaterAttenuationCoefficientReference(args.dir[0])
    water.calc_ref(args.detector)