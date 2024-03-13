import os
import pandas as pd


def merge(folder_path):
    combined_data = pd.DataFrame()

    for file_name in os.listdir(folder_path):
        if 'closePosition' in file_name and file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            df = pd.read_csv(file_path, usecols=['Key', 'ExitTime', 'Symbol', 'EntryPrice', 'Quantity', 'Pnl'])
            df['Date'] = pd.to_datetime(df['ExitTime']).dt.date
            combined_data = pd.concat([combined_data, df], ignore_index=True)


    combined_data.to_csv('combined_closePosition.csv', index=False)

def calculate(combined_data):
    total_trades = len(combined_data)
    unique_days = len(combined_data['Date'].unique())
    average_trades = total_trades / unique_days
    total_pnl = combined_data['Pnl'].sum()
    profit_trades = len(combined_data[combined_data['Pnl'] > 0])
    loss_trades = len(combined_data[combined_data['Pnl'] <= 0])

    with open('combined_stats.txt', 'w') as file:
        file.write(f'Total trades: {total_trades}\n')
        file.write(f'Unique days: {unique_days}\n')
        file.write(f'Average trades: {average_trades}\n')
        file.write(f'Total Pnl: {total_pnl}\n')
        file.write(f'Profit Trades: {profit_trades}\n')
        file.write(f'Loss Trades: {loss_trades}\n')

def calculate_streaks(combined_data, n):
    combined_data['Pnl_Sign'] = combined_data['Pnl'].apply(lambda x: 'Win' if x > 0 else 'Lose')
    combined_data['Streak_Group'] = (combined_data['Pnl_Sign'] != combined_data['Pnl_Sign'].shift()).cumsum()
    streaks = combined_data.groupby(['Pnl_Sign', 'Streak_Group']).agg(
        No_of_Trades=('Pnl_Sign', 'count'),
        Start_Date=('ExitTime', 'first'),
        End_Date=('ExitTime', 'last'),
        Pnl_of_Streak=('Pnl', 'sum')
    ).reset_index()

    top_winning_streaks = streaks[streaks['Pnl_Sign'] == 'Win'].nlargest(n, 'Pnl_of_Streak')
    top_losing_streaks = streaks[streaks['Pnl_Sign'] == 'Lose'].nsmallest(n, 'Pnl_of_Streak')

    with open('combined_winning_losing.txt', 'w') as file:
        file.write('Top {} winning streaks\n'.format(n))
        for i, row in top_winning_streaks.iterrows():
            file.write(f"{i + 1}) No. of Trades: {row['No_of_Trades']} "
                       f"Start Date - End Date: {row['Start_Date']} - {row['End_Date']} "
                       f"Pnl of Streak: {row['Pnl_of_Streak']}\n")

        file.write('\nTop {} losing streaks\n'.format(n))
        for i, row in top_losing_streaks.iterrows():
            file.write(f"{i + 1}) No. of Trades: {row['No_of_Trades']} "
                       f"Start Date - End Date: {row['Start_Date']} - {row['End_Date']} "
                       f"Pnl of Streak: {row['Pnl_of_Streak']}\n")



folder_path = '/Users/pratikmohanty/Desktop/python/SampleData/SampleData'
# Give your Folder Path
merge(folder_path)
n = int(input("Enter the value of n: "))

combined_data = pd.read_csv('combined_closePosition.csv')
calculate(combined_data)
calculate_streaks(combined_data, n)

