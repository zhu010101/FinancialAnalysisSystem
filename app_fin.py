from flask import Flask, request, render_template
import psycopg2
import pandas as pd
import plotly.graph_objects as go

app = Flask(__name__)

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def home():
    symbols = []
    if request.method == 'POST':
        try:
            # Get the selected symbols from the form
            selected_symbols = [request.form.get(f'symbol{i}') for i in range(1, 6) if request.form.get(f'symbol{i}')]

            # Connect to the PostgreSQL database
            conn = psycopg2.connect(
                host="localhost",
                database="stockStock",
                user="postgres",
                password="123"
            )
            # Create a cursor
            cur = conn.cursor()

            # Fetch historical price data for the selected symbol
            data_frames = []
            for symbol in selected_symbols:
                query = f"SELECT date, high, low, open, close FROM historical_price WHERE symbol = '{symbol}'"
                cur.execute(query) 
                rows = cur.fetchall()
                df = pd.DataFrame(rows, columns=['date', 'high', 'low', 'open', 'close'])
                data_frames.append(df)

            # Fetch financial ratios for the selected symbols
            query = "SELECT * FROM financial_ratios WHERE symbol IN %s"
            cur.execute(query, (tuple(selected_symbols),))
            ratios = cur.fetchall()

         # Fetch financial data for the selected symbols
            financial_metrics = {}
            for symbol in selected_symbols:

                # Fetch revenue and net profit from income statement table
                cur.execute(f"SELECT date, revenue, netincome FROM income_statement WHERE symbol = '{symbol}'")
                income_data = cur.fetchall()

                # Fetch free cash flow from cash flow statement table
                cur.execute(f"SELECT date, freecashflow FROM cashflow_statement WHERE symbol = '{symbol}'")
                cashflow_data = cur.fetchall()

                # Fetch total debt from balance sheet table
                cur.execute(f"SELECT date, totaldebt FROM balance_sheet WHERE symbol = '{symbol}'")
                balance_data = cur.fetchall()

                # Combine dates from all tables
                all_dates = set([row[0] for row in income_data] + [row[0] for row in cashflow_data] + [row[0] for row in balance_data])

                combined_data = {}
                for date in all_dates:
                    combined_data[date] = {
                        'revenue': next((row[1] for row in income_data if row[0] == date), None),
                        'net_profit': next((row[2] for row in income_data if row[0] == date), None),
                        'free_cash_flow': next((row[1] for row in cashflow_data if row[0] == date), None),
                        'total_debt': next((row[1] for row in balance_data if row[0] == date), None)
                    }
                financial_metrics[symbol] = combined_data

                # Create a new plot for financial data
                financial_fig = go.Figure()
                financial_fig.update_layout(title='Financial Metrics', yaxis_title='Value', barmode='group')

                for symbol, data in financial_metrics.items():
                    fig = go.Figure()

                    y_values_revenue = []
                    y_values_net_profit = []
                    y_values_free_cash_flow = []
                    y_values_total_debt = []

                    for values in data.values():
                        y_values_revenue.append(values['revenue'])
                        y_values_net_profit.append(values['net_profit'])
                        y_values_free_cash_flow.append(values['free_cash_flow'])
                        y_values_total_debt.append(values['total_debt'])

                    fig.add_trace(go.Bar(y=y_values_revenue, name=f'Revenue ({symbol})'))
                    fig.add_trace(go.Bar(y=y_values_net_profit, name=f'Net Profit ({symbol})'))
                    fig.add_trace(go.Bar(y=y_values_free_cash_flow, name=f'Free Cash Flow ({symbol})'))
                    fig.add_trace(go.Bar(y=y_values_total_debt, name=f'Total Debt ({symbol})'))

                    fig.update_layout(title=f'Financial Metrics ({symbol})', yaxis_title='Value', barmode='group')

                    financial_fig.add_traces(fig.data)

            # Calculate intrinsic value
            intrinsic_values = {}
            for symbol in selected_symbols:

            # Fetch free cash flow from cash flow statement table
                cur.execute(f"SELECT freecashflow FROM cashflow_statement WHERE symbol = '{symbol}'")
                cashflow_data = cur.fetchall()
                free_cash_flow = [row[0] for row in cashflow_data]

                # Calculate intrinsic value
                discount_rate = 0.1  # Example discount rate
                intrinsic_value = 0
                
                growth_rate = 0.05  # Example growth rate
                for i in range(len(free_cash_flow)):
                    intrinsic_value += free_cash_flow[i] / ((1 + discount_rate) ** (i + 1))
                terminal_value = (free_cash_flow[-1] * (1 + growth_rate)) / (discount_rate - growth_rate)
                intrinsic_value += terminal_value / ((1 + discount_rate) ** len(free_cash_flow))

                # Store intrinsic value
                intrinsic_values[symbol] = intrinsic_value
                
            # Close the cursor and connection
            cur.close()
            conn.close()

            # Fetch the industry and companies in the same industry for each selected symbol
            # Create a dictionary to store the ranks of selected symbols
            # Define selected_symbol_ranks as an empty dictionary
            selected_symbol_ranks = {}

            # Define tables_data as an empty list
            tables_data = []

            # Iterate over selected_symbols and calculate ranks
            for selected_symbol in selected_symbols:
                conn = psycopg2.connect(
                    host="localhost",
                    database="stockStock",
                    user="postgres",
                    password="123"
                )

                cur = conn.cursor()
                cur.execute(f"SELECT industry FROM company_profiles WHERE symbol = '{selected_symbol}'")
                industry_row = cur.fetchone()

                if industry_row is None:
                    app.logger.error(f"Symbol '{selected_symbol}' not found in company_profiles table")
                    continue
                industry = industry_row[0]

                cur.execute(f"SELECT symbol, companyname, industry, beta, mktcap FROM company_profiles WHERE industry = '{industry}'")
                companies = cur.fetchall()

                # Calculate rank based on market capitalization
                sorted_companies = sorted(companies, key=lambda x: x[4], reverse=True)

                # Assign rank and row rank to each company in the table data
                ranked_companies = []
                for idx, company in enumerate(sorted_companies, start=1):
                    rank = idx
                    row_rank = companies.index(company) + 1
                    ranked_companies.append(company + (rank, row_rank))

                    # Save rank of selected symbol
                    if company[0] == selected_symbol:
                        selected_symbol_ranks[selected_symbol] = rank

                cur.close()
                conn.close()

                # Append data for current symbol to tables_data
                tables_data.append({
                    'symbol': selected_symbol,
                    'companies': ranked_companies
                })

            # Render the results template with the retrieved data
            if data_frames:
                historical_graph_data = {}
                financial_graph_data = {}

                # Add historical price charts
                for symbol, df in zip(selected_symbols, data_frames):

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df['date'], y=df['high'], mode='lines', name='High', line=dict(color='red')))
                    fig.add_trace(go.Scatter(x=df['date'], y=df['low'], mode='lines', name='Low', line=dict(color='blue')))
                    fig.add_trace(go.Scatter(x=df['date'], y=df['open'], mode='lines', name='Open', line=dict(color='green')))
                    fig.add_trace(go.Scatter(x=df['date'], y=df['close'], mode='lines', name='Close', line=dict(color='orange')))
                    fig.update_layout(title=f'Historical Stock Prices ({symbol})', xaxis_title='Date', yaxis_title='Price', legend=dict(x=0, y=1.1, orientation='h'))
                    historical_graph_data[symbol] = fig.to_json()

                # Add financial metrics charts
                for symbol, data in financial_metrics.items():

                    fig = go.Figure()
                    y_values_revenue = []
                    y_values_net_profit = []
                    y_values_free_cash_flow = []
                    y_values_total_debt = []

                    for values in data.values():
                        y_values_revenue.append(values['revenue'])
                        y_values_net_profit.append(values['net_profit'])
                        y_values_free_cash_flow.append(values['free_cash_flow'])
                        y_values_total_debt.append(values['total_debt'])

                    fig.add_trace(go.Bar(y=y_values_revenue, name=f'Revenue ({symbol})'))
                    fig.add_trace(go.Bar(y=y_values_net_profit, name=f'Net Profit ({symbol})'))
                    fig.add_trace(go.Bar(y=y_values_free_cash_flow, name=f'Free Cash Flow ({symbol})'))
                    fig.add_trace(go.Bar(y=y_values_total_debt, name=f'Total Debt ({symbol})'))
                    fig.update_layout(title=f'Financial Metrics ({symbol})', yaxis_title='Value', barmode='group')
                    financial_graph_data[symbol] = fig.to_json()

                # Render the results template with the retrieved data
                return render_template("index.html", symbols=symbols, ratios=ratios, historical_graph_data=historical_graph_data,intrinsic_values=intrinsic_values, financial_graph_data=financial_graph_data,tables_data=tables_data,selected_symbol_ranks=selected_symbol_ranks)
            else:
                return render_template("index.html", symbols=symbols)

        except psycopg2.Error as e:
            # Log the error and return an error message
            app.logger.error(f"PostgreSQL error: {e}")
            return f"PostgreSQL error: {e}"
        
        except Exception as e:
            # Log the error and return an error message
            app.logger.error(f"An error occurred: {e}")
            return f"An error occurred while processing your request: {e}"

    # Fetch symbols from the database to populate the dropdowns
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="stockStock",
            user="postgres",
            password="123"
        )
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT symbol FROM financial_ratios")
        symbols = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()

    except psycopg2.Error as e:
        # Log the error and return an error message
        app.logger.error(f"PostgreSQL error: {e}")
        return f"PostgreSQL error: {e}"
    
    except Exception as e:
        # Log the error and return an error message
        app.logger.error(f"An error occurred: {e}")
        return f"An error occurred while fetching symbols: {e}"

    # Render the home page with the form
    return render_template("index.html", symbols=symbols)

if __name__ == '__main__':
    app.run(debug=True)