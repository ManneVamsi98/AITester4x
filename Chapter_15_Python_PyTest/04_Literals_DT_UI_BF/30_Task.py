# Task for the Today
# Take a 2 input from the user
# Print the Quotient and Remainder
# 15 ->  num1
# 2 -> num2
# Q -> 7
# R -> 1
input1 = int(input("Enter the first number: "))
input2 = int(input("Enter the second number: "))

quotient = input1 // input2
remainder = input1 % input2

print(f"Quotient: {quotient}")
print(f"Remainder: {remainder}")