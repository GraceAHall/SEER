
# import numpy as np
import pandas as pd
import unittest
import helpers

class TestVariableEncoding(unittest.TestCase):

    # def test_infer_dtype_1(self):
    #     inpval = pd.Series([0, 1, 2, 3, 4, 5, 6, 7])
    #     expect = 'int'
    #     actual = helpers._infer_numeric_dtype(inpval)
    #     self.assertEqual(actual, expect)
    
    # def test_infer_dtype_2(self):
    #     inpval = pd.Series([0.0, 1.0, 2, 3, 4, 5, 6, 7])
    #     expect = 'int'
    #     actual = helpers._infer_numeric_dtype(inpval)
    #     self.assertEqual(actual, expect)
    
    # def test_infer_dtype_3(self):
    #     inpval = pd.Series([0.1, 1.2, 2, 3, 4, 5, 6, 7])
    #     expect = 'float'
    #     actual = helpers._infer_numeric_dtype(inpval)
    #     self.assertEqual(actual, expect)

    def test_categorise2_1(self):
        inpval = pd.Series([0, 1, 2, 3, 4, 5, 6, 7])
        expect = [('low (0-3)', 0, 3), ('high (4-7)', 4, 7)]
        actual = helpers.categorise2(inpval)
        self.assertEqual(actual, expect)
    
    def test_categorise2_2(self):
        inpval = pd.Series([0, 1, 2, 3, 4, 5, 6, 7, 8])
        expect = [('low (0-4)', 0, 4), ('high (5-8)', 5, 8)]
        actual = helpers.categorise2(inpval)
        self.assertEqual(actual, expect)
    
    def test_categorise2_3(self):
        inpval = pd.Series([0, 0, 0, 0, 0, 1, 2, 2, 10])
        expect = [('low (0-0)', 0, 0), ('high (1-10)', 1, 10)]
        actual = helpers.categorise2(inpval)
        self.assertEqual(actual, expect)
    
    def test_categorise3_1(self):
        inpval = pd.Series([0, 1, 2, 3, 4.1, 5, 6, 7, 8])
        expect = [('low (0.0-2.0)', 0, 2), ('mid (3.0-5.0)', 3, 5), ('high (6.0-8.0)', 6, 8)]
        actual = helpers.categorise3(inpval)
        self.assertEqual(actual, expect)
    
    def test_categorise3_2(self):
        inpval = pd.Series([0, 0, 0, 3, 4, 5, 6, 6, 6])
        expect = [('low (0-0)', 0, 0), ('mid (3-5)', 3, 5), ('high (6-6)', 6, 6)]
        actual = helpers.categorise3(inpval)
        self.assertEqual(actual, expect)
    
    def test_categorise3_3(self):
        inpval = pd.Series([0, 0, 0, 0, 4, 5, 6, 7, 8])
        expect = [('low (0-0)', 0, 0), ('mid (4-5)', 4, 5), ('high (6-8)', 6, 8)]
        actual = helpers.categorise3(inpval)
        self.assertEqual(actual, expect)
    
    def test_categorise3_4(self):
        inpval = pd.Series([0, 1, 2, 3, 4, 5, 6, 7])
        expect = [('low (0-2)', 0, 2), ('mid (3-4)', 3, 4), ('high (5-7)', 5, 7)]
        actual = helpers.categorise3(inpval)
        self.assertEqual(actual, expect)
    
    def test_categorise3_5(self):
        inpval = pd.Series([0, 0, 0, 0, 4, 5, 5, 5])
        expect = [('low (0-0)', 0, 0), ('mid (4-4)', 4, 4), ('high (5-5)', 5, 5)]
        actual = helpers.categorise3(inpval)
        self.assertEqual(actual, expect)
    
    def test_categorise3_6(self):
        inpval = pd.Series([0, 0, 0, 4, 5, 5, 6])
        expect = [('low (0-0)', 0, 0), ('mid (4-4)', 4, 4), ('high (5-6)', 5, 6)]
        actual = helpers.categorise3(inpval)
        self.assertEqual(actual, expect)

    def test_numeric2categorical_1(self):
        inpval = pd.Series([0, 1, 2, 3, 4, 5, 6, 7, 8])
        catranges = helpers.categorise3(inpval)
        self.assertEqual(helpers.numeric2categorical(0, catranges), 'low (0-2)')
        self.assertEqual(helpers.numeric2categorical(1, catranges), 'low (0-2)')
        self.assertEqual(helpers.numeric2categorical(2, catranges), 'low (0-2)')
        self.assertEqual(helpers.numeric2categorical(3, catranges), 'mid (3-5)')
        self.assertEqual(helpers.numeric2categorical(4, catranges), 'mid (3-5)')
        self.assertEqual(helpers.numeric2categorical(5, catranges), 'mid (3-5)')
        self.assertEqual(helpers.numeric2categorical(6, catranges), 'high (6-8)')
        self.assertEqual(helpers.numeric2categorical(7, catranges), 'high (6-8)')
        self.assertEqual(helpers.numeric2categorical(8, catranges), 'high (6-8)')
    
    def test_numeric2categorical_2(self):
        inpval = pd.Series([0, 0, 0, 0, 4, 5, 5, 5])
        catranges = helpers.categorise3(inpval)
        self.assertEqual(helpers.numeric2categorical(0, catranges), 'low (0-0)')
        self.assertEqual(helpers.numeric2categorical(4, catranges), 'mid (4-4)')
        self.assertEqual(helpers.numeric2categorical(5, catranges), 'high (5-5)')
        self.assertRaises(ValueError, helpers.numeric2categorical, 1, catranges)

        
if __name__ == '__main__':
    unittest.main()