def my_function(a, b, c):
    """
    This is my function. There are many like it, but this is mine.
    """
    return a + b + c


my_function(1, 2, 3)

arguments = [1, 2, 3]
my_function(*arguments)

#####

dic

keyword_arguments = {"a": 1, "b": 2, "c": 3}
my_function(**keyword_arguments)

######

my_function(1, 2, c=3)

args = [1, 2]
kwargs = {"c": 3}
my_function(*args, **kwargs)


########


lookup_dict = {
    "Calculate": my_calculate_func,
    "Balance": my_balance_func,
}

kwargs = {"default": 5}
if "maximum" in cli_arguments:
    kwargs["maximum"] = cli_arguments["maximum"]

lookup_dict["type"](**kwargs)

#######

custom_data = {
    "product": "clinker",
    "quantity": 5.2,
    "measurement": "kilogram"
}
custom_data["product"]


class CustomData(object):
    def __init__(product, quantity, measurement="kilogram"):
        self.product = product
        self.quantity = quantity
        self.measurement = measurement

custom_data = CustomData("clinker", 5.2)
custom_data2 = CustomData("meal", 6)
custom_data.product

chain  = {"clinker": custom_data("clinker, 5.2"), 'meal': custom_data("meal", 6)}

user_data = [
    ("clinker", 5.2),
    ("meal", 6),
    ("cement", 12),
]
chain = []
for product, quantity in user_data:
    chain.append(CustomData(product, quantity))

chain_list = [CustomData(product, quantity) for product, quantity in user_data]
chain_dict = {product: CustomData(product, quantity) for product, quantity in user_data}
