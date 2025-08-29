import os
import numpy as np
import pandas as pd

import pfs.ga.common
from pfs.ga.common.io import DataFrameSerializer

from ..test_base import TestBase

class DataFrameSerializerTest(TestBase):
    def get_test_data(self):
        fn = self.get_test_data_file('test/obs.feather')
        return pd.read_feather(fn)
    
    def test_init(self):
        s = DataFrameSerializer()

    def test_read_csv(self):
        fn = self.get_test_data_file('test/sample.csv')
        s = DataFrameSerializer()
        df = s.read(fn)

    def test_write_csv(self):
        df = self.get_test_data()
        fn = self.get_test_temp_file(self.get_filename('.csv'))
        
        s = DataFrameSerializer(mask=np.s_[:1000])
        s.write(df, fn)

    def test_read_feather(self):
        fn = self.get_test_data_file('test/sample.feather')
        s = DataFrameSerializer()
        df = s.read(fn)

    def test_write_feather(self):
        df = self.get_test_data()
        fn = self.get_test_temp_file(self.get_filename('.feather'))
        
        s = DataFrameSerializer(mask=np.s_[:1000])
        s.write(df, fn)

    def test_read_hdf5(self):
        fn = self.get_test_data_file('test/sample.h5')
        s = DataFrameSerializer()
        df = s.read(fn)

    def test_write_hdf5(self):
        df = self.get_test_data()
        fn = self.get_test_temp_file(self.get_filename('.h5'))
        
        s = DataFrameSerializer(mask=np.s_[:1000])
        s.write(df, fn)