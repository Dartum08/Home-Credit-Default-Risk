# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 22:30:40 2019

@author: Arun
"""

# pandas and numpy for data manipulation
import pandas as pd
import numpy as np

# featuretools for automated feature engineering
import featuretools as ft

# matplotlit and seaborn for visualizations
import matplotlib.pyplot as plt
plt.rcParams['font.size'] = 22
import seaborn as sns

# Suppress warnings from pandas
import warnings
warnings.filterwarnings('ignore')

# sklearn preprocessing for dealing with categorical variables
from sklearn.preprocessing import LabelEncoder

# File system manangement
import os

# Suppress warnings 
import warnings
warnings.filterwarnings('ignore')

# matplotlib and seaborn for plotting
import matplotlib.pyplot as plt
import seaborn as sns

app_train = pd.read_csv('application_train.csv')

app_test = pd.read_csv('application_test.csv')

app_train['TARGET'].value_counts()

mis_val = app_train.isnull().sum()
len(app_train)

# Function to calculate missing values by column# Funct 
def missing_values_table(df):
        # Total missing values
        mis_val = df.isnull().sum()
        
        # Percentage of missing values
        mis_val_percent = 100 * df.isnull().sum() / len(df)
        
        # Make a table with the results
        mis_val_table = pd.concat([mis_val, mis_val_percent], axis=1)
        
        # Rename the columns
        mis_val_table_ren_columns = mis_val_table.rename(
        columns = {0 : 'Missing Values', 1 : '% of Total Values'})
        
        # Sort the table by percentage of missing descending
        mis_val_table_ren_columns = mis_val_table_ren_columns[
            mis_val_table_ren_columns.iloc[:,1] != 0].sort_values(
        '% of Total Values', ascending=False).round(1)
        
        # Print some summary information
        print ("Your selected dataframe has " + str(df.shape[1]) + " columns.\n"      
            "There are " + str(mis_val_table_ren_columns.shape[0]) +
              " columns that have missing values.")
        
        # Return the dataframe with missing information
        return mis_val_table_ren_columns
    
#Missing value statistics
missing_values = missing_values_table(app_train)
app_train.dtypes.value_counts()        

# Number of unique classes in each object column
app_train.select_dtypes('object').apply(pd.Series.nunique, axis=0)

# Create a label encoder object
le = LabelEncoder()
le_count = 0

# Iterate through the columns
for col in app_train:
    if app_train[col].dtype == 'object':
        # If 2 or fewer unique categories
        if len(app_train[col].unique()) <= 2:
            # Train on the training data
            le.fit(app_train[col])
            # Transform both training and testing data
            app_train[col] = le.transform(app_train[col])
            app_test[col] = le.transform(app_test[col])
            
            # Keep track of how many columns were label encoded
            le_count += 1
            
print('%d columns were label encoded.' % le_count)

# one-hot encoding of categorical variables
app_train = pd.get_dummies(app_train)
app_test = pd.get_dummies(app_test)

train_labels = app_train['TARGET']

# Align the training and testing data, keep only columns present in both dataframes
app_train, app_test = app_train.align(app_test, join = 'inner', axis = 1)

# Add the target back in
app_train['TARGET'] = train_labels

(app_train['DAYS_BIRTH']/-365).describe()
app_train['DAYS_EMPLOYED'].describe()

app_train['DAYS_EMPLOYED'].plot.hist()
anom = app_train[app_train['DAYS_EMPLOYED'] == 365243]
nanom = app_train[app_train['DAYS_EMPLOYED'] != 365243]

# Create an anomalous flag column
app_train['DAYS_EMPLOYED_ANOM'] = app_train['DAYS_EMPLOYED'] == 365243

#Replace anomalous value with nan
app_train['DAYS_EMPLOYED'].replace({365243:np.nan}, inplace=True)

app_train['DAYS_EMPLOYED'].plot.hist(title = 'Days Employment Histogram');
plt.xlabel('Days Employment');

app_test['DAYS_EMPLOYED_ANOM'] = app_test["DAYS_EMPLOYED"] == 365243
app_test["DAYS_EMPLOYED"].replace({365243: np.nan}, inplace = True)

print('There are %d anomalies in the test data out of %d entries' 
      % (app_test["DAYS_EMPLOYED_ANOM"].sum(), len(app_test)))

app_train.describe()

correlations = app_train.corr()['TARGET'].sort_values(ascending=False)
hc = correlations[correlations['TARGET'] >= 0.5]

# Find the correlation of the positive days since birth and target
app_train['DAYS_BIRTH'] = abs(app_train['DAYS_BIRTH'])
app_train['DAYS_BIRTH'].corr(app_train['TARGET'])

# KDE plot of loans that were repaid on time
sns.kdeplot(app_train.loc[app_train['TARGET'] == 0, 'DAYS_BIRTH'] / 365, label = 'target == 0')

# KDE plot of loans which were not repaid on time
sns.kdeplot(app_train.loc[app_train['TARGET'] == 1, 'DAYS_BIRTH'] / 365, label = 'target == 1')

# Labeling of plot
plt.xlabel('Age (years)'); plt.ylabel('Density'); plt.title('Distribution of Ages');

#sns.kdeplot(app_train['TARGET'] == 1, app_train['DAYS_BIRTH']/365)

app_data = app_train[['TARGET', 'DAYS_BIRTH']]
app_data['YEARS_BIRTH'] = app_data['DAYS_BIRTH'] /365

app_data['YEARS_BINNED'] = pd.cut(app_data['YEARS_BIRTH'], np.linspace(20,70,num=11))

# Group by the bin and calculate averages
app_groups = app_data.groupby('YEARS_BINNED').mean()
app_groups.head(5)

# Group by the bin and calculate averages
ext_data = app_train[['TARGET', 'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3', 
                      'DAYS_BIRTH']]
ext_data_corrs = ext_data.corr()
ext_data_corrs

#Feature Eng
# Make a new dataframe for polynomial features

poly_features = app_train[['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3', 'DAYS_BIRTH']]
poly_features_test = app_test[['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3', 'DAYS_BIRTH']]

# imputer for handling missing values
from sklearn.preprocessing import Imputer
imputer = Imputer(strategy='median')

poly_target = app_train['TARGET']

# Need to impute missing values
poly_features = imputer.fit_transform(poly_features)
poly_features_test = imputer.transform(poly_features_test)

# Create the polynomial object with specified degree
from sklearn.preprocessing import PolynomialFeatures
poly_transformer = PolynomialFeatures(degree=3)

# Train the polynomial features
poly_transformer.fit(poly_features)

poly_features = poly_transformer.transform(poly_features)
poly_features_test = poly_transformer.transform(poly_features_test)

Columns = poly_transformer.get_feature_names(input_features = ['EXT_SOURCE_1', 
                        'EXT_SOURCE_2', 'EXT_SOURCE_3', 'DAYS_BIRTH'])
# Create a dataframe of the features 
poly_features = pd.DataFrame(poly_features, columns = Columns)

# Add in the Target Variable
poly_features['TARGET'] = poly_target

# Find the correlations with Target variable
poly_corrs = poly_features.corr()['TARGET'].sort_values()

# Put test features into dataframe
poly_features_test = pd.DataFrame(poly_features_test, columns = Columns)

# Merge polynomial features into training dataframe
poly_features['SK_ID_CURR'] = app_train['SK_ID_CURR']
app_train_poly = app_train.merge(poly_features, on = 'SK_ID_CURR', how = 'left')

# Merge polnomial features into testing dataframe
poly_features_test['SK_ID_CURR'] = app_test['SK_ID_CURR']
app_test_poly = app_test.merge(poly_features_test, on = 'SK_ID_CURR', how = 'left')

# Align the dataframes
app_train_poly, app_test_poly = app_train_poly.align(app_test_poly, join = 'inner',
                                                     axis = 1)



















