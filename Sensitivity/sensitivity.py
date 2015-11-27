import os
import numpy as np

"""
Pseudo OT sensitivity calculator
    2014/11/08  ahirota
"""

dtor = np.pi / 180.
const_c = 2.99792458e8
const_k = 1.38e-23
const_h = 6.626e-34
bandDefinitions = {
    1: [31.3e9, 45e9],
    2: [67.0e9, 84e9],
    3: [84.0e9, 116e9],
    4: [125.e9, 163e9],
    5: [163.e9, 211e9],
    6: [211.e9, 275e9],
    7: [275.e9, 373e9],
    8: [385.e9, 500e9],
    9: [602.e9, 720e9],
    10: [787e9, 950e9],
}

path = os.environ['HOME']


def planck(freq, T):
    """
    Parameters
    ----------
    freq : [Hz]
    T    : [K]
    """
    tmp = const_h * freq / const_k
    return tmp / (np.exp(tmp / T) - 1.0)


def getReceiverBand(frequency):
    """
    Parameters
    ----------
    frequency : [Hz]
    """
    for band in range(1, 11):
        freq0, freq1 = bandDefinitions[band]
        if frequency >= freq0 and frequency <= freq1:
            return band
    raise Exception("Invalid frequency [%s]" % (frequency))


def getReceiverTemperature(band):
    """
    Based on ReceiverTemperature.java

    Parameters
    ----------
    band : Integer

    """
    d = dict()
    d[1] = 17.
    d[2] = 30.
    d[3] = 45.
    d[4] = 51.
    d[5] = 65.
    d[6] = 55.
    d[7] = 75.
    d[8] = 150.
    d[9] = 110.
    d[10] = 230.
    return d[band]


def readATMFile(infile):
    infile_ = os.path.expanduser(infile)
    with file(infile_) as f:
        lines = [l.strip() for l in f.readlines()]
    values = []
    for iLine, line in enumerate(lines):
        if line.startswith('#'):
            continue
        tokens = line.split(' ')
        if len(tokens) != 3:
            raise Exception('Unsupported file format [%s] [L%d:"%s"]' % (infile_, iLine, line))
        values.append(tokens)
    values = np.array(values, dtype=float)
    return values


class SensitivityCalculator:
    """
    Simple copy of OT sensitivity calculator.

    Example
    -------
        from os import path
        from AcsutilPy.FindFile import findFile
        configDir = path.split(findFile('config/SKY.SPE0001.trim')[0])[0]
        s = SensitivityCalculator(configDir=configDir)
        latitude  = -23.029
        dec = -22.
        v = s.calcSensitivity(5.186, 115e9, dec=dec, latitude=latitude, N_pol=2,
                              N=32., BW=1.e9, D=12.)
        print v * 1.0e3
    0.50284
    """

    def __init__(self, config_dir=".", load_all=False):
        """
        Parameters
        ----------
        config_dir :
            Directory which stores ATM parameter files.

        load_all :
            If specified (bool), load all the ATM parameter files
            while initializing the instance. Otherwise, loading
            will be delayed.

        """
        self._configDir = config_dir
        self._atmospheresFileName = [
            "SKY.SPE0001.trim",
            "SKY.SPE0002.trim",
            "SKY.SPE0003.trim",
            "SKY.SPE0004.trim",
            "SKY.SPE0005.trim",
            "SKY.SPE0006.trim",
            "SKY.SPE0007.trim",
        ]
        self.WV_MAP_VALUES = [
            0.472,
            0.658,
            0.913,
            1.262,
            1.796,
            2.748,
            5.186,
        ]
        self._atmdata = dict()
        if load_all:
            for pwv in self.WV_MAP_VALUES:
                self._load(pwv)

    def get_available_pwvs(self):
        return self.WV_MAP_VALUES

    def lookup(self, pwv, freq):
        if pwv not in self._atmdata:
            self._load(pwv)
        d = self._atmdata[pwv]
        inp_freq = np.argmin(np.abs(d['freq'] - freq / 1.0e9))
        return d['tau0'][inp_freq], d['Tsky'][inp_freq]

    def _load(self, pwv):
        """
        Load total zenith opacity and atmospheric temperature
        from ATM model file
        """
        # select octile
        iPWV = self.WV_MAP_VALUES.index(pwv)
        fileName = self._atmospheresFileName[iPWV]
        fileName = os.path.join(self._configDir, fileName)
        d = readATMFile(fileName)
        freq, tau0, Tsky = d.transpose()
        self._atmdata[pwv] = dict(freq=freq, tau0=tau0, Tsky=Tsky)

    def get_tsys(self, pwv, freq, el=None, dec=None, latitude=None,
                 verbose=False, return_full=False):
        """
        dec [deg]
        latitude [deg]
        pwv [mm]
        freq [Hz]
        :param return_full:
        :param verbose:
        :param latitude:
        :param dec:
        :param el:
        :param freq:
        :param pwv:
        """
        Tamb = 270  # Ambient temperature (260 - 280 K)
        eta_feed = 0.95  # Forward efficiency
        tau0, Tsky = self.lookup(pwv, freq)

        # airmass
        if el:
            airmass = 1. / np.sin(el * dtor)
        else:
            sinDec = np.sin(dec * dtor)
            cosDec = np.cos(dec * dtor)
            sinLat = np.sin(latitude * dtor)
            cosLat = np.cos(latitude * dtor)
            # HA=0.
            sinAltitude = sinDec * sinLat + cosDec * cosLat
            airmass = 1.0 / sinAltitude
        band = getReceiverBand(freq)
        # Receiver temperature
        Trx = getReceiverTemperature(band)
        # sideband gain ratio
        gr = 0. if freq < 600.e9 else 1.

        Tsky_atmp = planck(freq, Tsky)
        Tamb = planck(freq, Tamb)

        # Calculate Tsky along line of sight
        Tsky_z = Tsky_atmp * (1. - np.exp(-tau0 * airmass)) / \
                             (1. - np.exp(-tau0))
        if verbose:
            for key in ['tau0', 'Tsky', 'Tamb', 'Trx']:
                v = eval(key)
                print "%-8s = %f" % (key, v)

        Tsys = Trx + Tsky_z * eta_feed + Tamb * (1. - eta_feed)
        Tsys = Tsys * np.exp(tau0 * airmass) / eta_feed * (1. + gr)

        if return_full:
            return dict(Tsys=Tsys,
                        Trx=Trx,
                        Tsky=Tsky,
                        Tsky_z=Tsky_z,
                        tau0=tau0,
                        airmass=airmass,
                        freq=freq,
                        pwv=pwv,
                        band=band,
                        el=el,
            )
        return Tsys

    def calcSensitivity(self, pwv, freq,
                        el=None,
                        dec=None, latitude=None,
                        tint=60., BW=1.0e9, N=32.,
                        N_pol=1., D=12.,
                        mode="image",
                        returnFull=False,
                        isSingleDish=False):
        """
        Calculate sensitivity

        Parameters
        ----------
        el : Elevation of the target source in [deg].
        dec : Dec of the target source in [deg].
              Required, if 'el' is not specified.
        latitude : Latitude of the observatory in [deg].
                   Required, if 'el' is not specified.
        t_int : Integration time [sec]
        BW : Bandwidth [Hz]
        N : Number of antennas
        N_pol : Number of polarizations
        D : Antenna diameter [m]
        mode : image, baseline, or antenna
            'image' - Imaging sensitivity
            'baseline' - Fringe sensitivity
            'antena' -> Antenna based gain solution sensitivity

        returnFull : If specified, returns a dictionary
                     which stores all the relevant information.
                     Otherwise, just returns sensitivity in [Jy].
        """

        if isSingleDish:
            print '[WARNING] [IsSingleDish] switch is deprecated'

        correlatorEfficiency = 0.88 * 0.96
        # atmosphericDecorrelationCoeff
        atmDecorrCoeff = 1.
        # instrumentalDecorrelationCoeff
        instDecorrCoeff = 1.

        # Tsys
        d = self.get_tsys(pwv, freq, el=el, dec=dec, latitude=latitude,
                          return_full=True)
        Tsys = d['Tsys']

        # Area
        A = np.pi * (D / 2.) ** 2
        # Surface accuracy (spec values)
        sigma = 25e-6 if D > 10 else 20e-6
        eta_A = 0.72 * np.exp(-16. * (np.pi * sigma / (const_c / freq)) ** 2)
        # Antenna efficiency
        rho_e = 2. * const_k / (eta_A * A)
        # [Jy]
        SEFD = Tsys * rho_e * 1.0e26

        efficiencies = atmDecorrCoeff * correlatorEfficiency * instDecorrCoeff

        # Single antenna sensitivity [Jy]
        s0 = SEFD / efficiencies / np.sqrt(N_pol * tint * BW)

        # Calculate sensitivity in Jy
        if mode == "sd_image":
            s = s0 / np.sqrt(N)
        elif mode == "image":
            if N >= 2:
                N_bl = N * (N - 1.) / 2.
                s = s0 / np.sqrt(2. * N_bl)
            else:
                s = s0
        elif mode == "baseline":
            # Sensitivity per a baseline
            s = s0 / np.sqrt(2.)
        elif mode == "antenna":
            # Antenna-based gain solution sensitivity
            # (Sensitivity which gives gain error of unity)
            if N >= 4:
                s = s0 / np.sqrt(2. * (N - 3.))
            else:
                s = s0  # For 2-antenna pointing observation, we can divide it by sqrt(2).
        else:
            raise Exception('Invalid mode [%s] specified' % mode)

        if returnFull:
            d['eta_A'] = eta_A
            d['SEFD'] = SEFD
            d['sensitivity'] = s
            d['BW'] = BW
            d['tint'] = tint
            d['N_pol'] = N_pol
            d['N'] = N
            d['D'] = D
            d['mode'] = mode
            return d
        else:
            return s

    def selecticAutomaticPWV(self, freq, el, timeIncrease=1.5):
        tList = []
        for iPWV, pwv in enumerate(self.WV_MAP_VALUES):
            s = self.calcSensitivity(pwv, freq, el=el,
                                     tint=1., BW=15.e9,
                                     N=50, D=12.)
            # Time required to achieve 1Jy sensitivity
            t = (s / 1.) ** 2
            tList.append(t)

        # Get the highest PWV which is within facor of
        # 'timeIncrease' in integration time
        w = np.where(tList < tList[0] * timeIncrease)
        iSelected = w[0][-1]
        pwv = self.WV_MAP_VALUES[iSelected]
        return pwv


def _test(opts):
    # /ALMA-10_6_0-B/OBSPREP/ObservingTool/src/alma/observatorycharacteristics/site/
    latitude = -23.029
    longitude = -67.754

    print "performing simple tests..."

    configDir = "." if opts.dir is None else opts.dir
    tsc = SensitivityCalculator(config_dir=configDir)

    dec = -22.
    print "[1] automatic PWV selection tests..."
    paramList = [
        [115.e9, 90, 5.186],
        [115.e9, 30, 2.748],
    ]
    for freq, el, pwv_expected in paramList:
        pwv = tsc.selecticAutomaticPWV(freq, el=el)
        print "Freq=%7.2f GHz El=%5.1f [deg] -> PWV=%f [expected=%f]" % \
            (freq / 1.0e9, el, pwv, pwv_expected)
        assert(pwv == pwv_expected)

    paramList = [
        [5.186, 80.e9, 0.23393],
        [5.186, 115e9, 0.50284],
        [1.262, 230e9, 0.36854],
        [1.262, 251e9, 0.38670],
        [0.913, 345e9, 0.63490],
        [0.472, 492e9, 2.45195],
        [0.472, 720e9, 15.9761738724],
    ]
    print "[2] Sensitivity calculation tests.... [interferometer]"
    for pwv, freq, v_expected in paramList:
        v = tsc.calcSensitivity(pwv, freq, dec=dec, latitude=latitude,
                                N_pol=2, N=32., BW=1.e9, D=12.) * 1.0e3
        print "v=%10.5f v_expected=%10.5f" % (v, v_expected)
        assert(np.abs(v / v_expected - 1.) < 1.0e-4)

    print "[3] Sensitivity calculation test... [single dish]"
    paramList = [
        [5.186, 80.e9, 5.20998],
        [5.186, 115e9, 11.19874],
        [0.913, 345e9, 14.13992],
        [0.472, 720e9, 355.80512],
    ]
    for pwv, freq, v_expected in paramList:
        v = tsc.calcSensitivity(pwv, freq, dec=dec, latitude=latitude,
                                N_pol=2, N=2., BW=1.e9, D=12.) * 1.0e3
        print "v=%10.5f v_expected=%10.5f" % (v, v_expected)
        assert(np.abs(v / v_expected - 1.) < 1.0e-4)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('-d', '--dir',
                      help="config directory which stores ATM data")
    parser.add_option('-t', '--test', action="store_true")
    opts, args = parser.parse_args()

    if opts.test:   # For test
        _test(opts)
