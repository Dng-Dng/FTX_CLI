import sys
import ccxt
from pprint import pprint

# replace with your key / secret
# key =  
# secret = 

exchange = ccxt.ftx({
    'apiKey': key,
    'secret': secret
})
#exchange.load_markets()
#print(exchange.symbols)

# create and execute a basic order
def simple_order():
    # params for the order
    params = {'postOnly': True}
    # send the order
    res = exchange.create_order("PERP-PERP", "limit", "buy", 1, 16, params)
    pprint(res)

# cancel all open orders for symbol
def cancel_all(symbol):
    res = exchange.cancel_all_orders(symbol)
    pprint(res)

#dollar to contracts
def dollar_convert(dollar, price):
    return round(dollar/price,4)

# create and execute a scaled order
def scaled_order(symbol, side, total_dollar, start_price, end_price, num_orders):
    
    #symbol: same as ftx e.g. BTC-PERP (in caps!)
    #side: buy/sell
    #dollar_total: total order size in $
    #start_price:
    #end_price:
    #num_orders: number of orders to split the price range
    
    # cast command line args to proper types for math
    symbol = symbol.upper()
    total_dollar = float(total_dollar)
    start_price = float(start_price)
    end_price = float(end_price)
    num_orders = int(num_orders)

    # params for the order
    params = {'postOnly': True}

    # size of each order
    # order_amount = total / num_orders

    # step size of each order price starting from start_price
    step_size = (end_price-start_price)/(num_orders-1)

    # loop to generate orders
    for order_num in range(num_orders):
        # the price of this order, using step_size to calculate offset
        order_price = start_price + step_size*order_num
        # send the order
        order_amount = dollar_convert(round(total_dollar/num_orders,4), order_price)
        res = exchange.create_order(symbol, "limit", side, order_amount, order_price, params)
        pprint(res)

def limit_chaser(symbol, side, amount, offset=200):
    side = side.lower()

    # params for the order
    params = {'postOnly': True}

    # current order we are using to chase with
    last_order = None

    # amount remaining to fill incase of partial fills along the way
    remaining = amount

    # loop to place / update order
    try:
        while(True):
            # get the top of the book
            top_of_book = get_top_of_book(symbol)
            if (side == "sell"):
                # set the order price adjusted for offset
                price = top_of_book[0] + offset
                # if we dont have an order yet place one
                if (not last_order):
                    last_order = exchange.create_order(symbol, "limit", side, remaining, price, params)
                # get last order again in case it has closed
                else:
                    last_order = exchange.fetch_order(last_order["id"])
                # if closed, done. return
                if last_order["status"] == "closed":
                    return
                # if the top bid adjusted for offset is above price, we need to update order
                if top_of_book[0] + offset  < last_order["price"]:
                    print("resubmitting order")
                    # cancel the order
                    exchange.cancel_order(last_order["id"])
                    # refetch to update remaining incase of partial fills between last fetch and now
                    last_order = exchange.fetch_order(last_order["id"])
                    remaining = last_order["remaining"]
                    # create new order
                    last_order = exchange.create_order(symbol, "limit", side, remaining, price, params)

            # logic same as above but inverted
            elif (side == "buy"):
                price = top_of_book[1] - offset
                if (not last_order):
                    last_order = exchange.create_order(symbol, "limit", side, remaining, price, params)
                else:
                    last_order = exchange.fetch_order(last_order["id"])
                if last_order["status"] == "closed":
                    return
                if top_of_book[1] - offset  > last_order["price"]:
                    print("resubmitting order")
                    exchange.cancel_order(last_order["id"])
                    last_order = exchange.fetch_order(last_order["id"])
                    remaining = last_order["remaining"]
                    last_order = exchange.create_order(symbol, "limit", side, remaining, price, params)
        time.sleep(2)
    #
    except KeyboardInterrupt as e:
        if (last_order):
            exchange.cancel_order(last_order["id"])
        raise e
    except Exception as e:
        if (last_order):
            exchange.cancel_order(last_order["id"])
        raise e

######### orders to be added ########

#def distribution order():
    #similar to a scaled order but the intervals are not of equal size.
    #may need to add some distribution to the interval

#def twap():

def pairs_order():
    # initiate an order for a pairs trade e.g. long btc-perp and short eth-perp
    # total size and % of total for each leg
    # How to execute

# parse function name and args and call function
def main():
    # name of function
    func_name = sys.argv[1]
    # args passed to function
    args = sys.argv[2:]
    # calling the function
    globals()[func_name](*args)

if __name__ == "__main__":
    main()