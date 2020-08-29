import pandas

# Create a Pandas dataframe from the data.
df = pandas.DataFrame({'Data': [10, 20, 30, 20, 15, 30, 45]})
print(type(df))
# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pandas.ExcelWriter('pandas_simple.xlsx', engine='xlsxwriter')
# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(writer, sheet_name='Sheet1')
# Close the Pandas Excel writer and output the Excel file.
writer.save()