class prompts:
    CODE_BEGINS = "# CODE BEGINS\n"
    CODE_ENDS = "\n# CODE ENDS"

    REVIEW_PROMPT = """
You are a code reviewer for Arduino IDE
Check the code whether it has ...
1. has any Serial.print() or Serial.println()
2. can be optimized by Direct Port Access if it has digitalWrite() and digitalRead() operations
3. can be optimized by Periodic Task Optimization if it has delay() operations by replacing it with millis() or micros(), if it has no delay() there is no need for this optimization
There are some code that are meant to run as fast as possible, do not mark them as periodic task
4. be optimized by replacing floating point numbers with fixed point numbers

If the optimization are already in place, do not optimize again, say False in your output
True, means there is still room for optimization 
If it is not Arduno code, output False in the Arduino_Code field
Output your by wrapping it in json format
    
{"Arduino_Code" : "True or False"
"optimizeSerial":"True or False"
"optimizeDPA" : "True or False"
"optimizePeriodicTask" : "True or False"
"optimize_fp_math": "True or False"}
Do not include any explanation
"""


    DPA_MACRO = """
#define SET_PIN_HIGH(port, pin) (PORT ## port |= (1 << pin))
#define SET_PIN_LOW(port, pin) ((PORT ## port) &= ~(1 << (pin)))
#define PIN_READ(port, pin) (PIN ## port & (1 << pin))\n
"""

    DPA_PROMPT_UNO = """
You are a code optimization tool for Arduino IDE. You will digitalWrite() and digitalRead() using direct port access
Please give me only the for. No explanation, just the code.
Board: Arduino Uno
Port on ATmega328P -> Arduino pin 
PD0->0
PD1->1
PD2->2
PD3->3
PD4->4
PD5->5
PD6->6
PD7->7
PB0->8
PB1->9
PB2->10
PB3->11
PB4->12
PB5->13
PC0->A0
PC1->A1
PC2->A2
PC3->A3
PC4->A4
PC5->A5
Use the following C macro which is defined at the start of the codes
#define SET_PIN_HIGH(port, pin) (PORT ## port |= (1 << pin))
#define SET_PIN_LOW(port, pin) ((PORT ## port) &= ~(1 << (pin)))
#define PIN_READ(port, pin) (PIN ## port & (1 << pin))
Use these macro to implement direct port access
If there are multiple digitalWrite(), combine them into a single bitmask, do not use the macro
Do not touch the pinMode() function
Do not use DDRX = to optimize declaring the pins
"""

    PERIODIC_TASK_PROMPT = """
You are a code optimization tool for Arduino IDE.
You will optimize by the code, by changing periodic tasks from using delay() to using millis() and micros()
First, identify the periodic tasks
Please give me only the code. No explanation, just the code.

The previousMillis variable is proviced and declared as a global variable
unsigned long previousMillis = 0;

The currentMillis variable is not provided and should be declared as a local variable
Add this variable at the start of the where the polling is done
unsigned long currentMillis = millis();

Minimize the use of digitalRead() by storing the last known state of the pin to optimize performance
"""

    INT_MATH_PROMPT="""
You are a code optimization tool for Arduino IDE.
There are fixed point (fp) math implementation in the code supplied below
There are macros to implement fp math in the code already

Follow the rules below:

# Context of the code provided
Fixed point is defined as fp. fp does not stand for floating point
We are using int32_t, 32 bits for the integer math implementation.
Replace the floating point operation with the fixed point math equivalent.
Do not modify the macros of the fixed point math implementation

# What to do with Float variables
Minimize the use of conversion functions like fp_to_float() and float_to_fp() as it defeats the pursose of fixed point math.
if they are originally float, redelare them with fp_int_t
// Example:
float num1 = 10.50;
// Replace with:
fp_int_t = float_to_fp(10.50);

# Integers Variables
For integer variables that have a type cast to float, (float), you may replace it with the macro FP_FROM_INT
Check the declaration of each variable, if they are originally integer, use the macro FP_FROM_INT
You may need to redefine some constant that are originally float. Change them to fixed point if neccessary
// Example:
int num4 = 10 
float num5 = num4 + 99.9;
// Replace with 
fp_int_t num4 = FP_FROM_INT(10L); // Append L to literals
fp_int_t num5 = num4 + float_to_fp(99.9)

For places such as for loops, check if the operation is just normal integre math or not
Do not use FP_FROM_INT() at the #define macros, but use them at the inline code when there is a need for conversion

# Arithmetic operation
Replace all multiplication and division * / operation with the function fp_mul() and fp_div()
There can be no * and / in the final code
Be careful of the order of operations

// Example
int a = b / c;
int e = b * c;
// Change to 
fp_num_t a = fp_div(b, c);
fp_num_t e = fp_mul(b, c);

# Literals and constants
By default, the literals on arduino are treated as 2 bytes. So add a use the macro FP_FROM_INT() that will automatically cast them to 4 bytes
Add a L literal ro every constants that are involved in the fixed point calculation
Do not append L to constants that are not related

// Example:
#define CONSTANT_1 2390
// Replace with
#define CONSTANT_1 2390L

# What to convert to FP math    
For code that only run once such as those in setup() it is fine to use float as it does not impact performance greatly
For values that are calculated once but used throughout the code, such as calibration data, you may first calculate them using float, then create another variable to store the fixed point representation  

# Integer values smaller than int32_t
Redeclare integers that are smaller than 32 bits like int8_t and int16_t to int32_t.
Cast integers that have smaller size than 32 bits to int32_t before using the FP_FROM_INT macro to convert them to Fixed point

int16_t num2 = 15;
fp_int_t num3 = FP_FROM_INT((fp_int_t)num2) //Case integers smaller than 32 bits to fp_int_t before bit shifting

# Output
Return every line of the optimized code
Do not include explanation for the code
Return the code with the FP macros

Below is the list of variables, functions and constants that need to be modified
Modify accordingly, do not touch ot

"""

    FP_MATH_MACRO="""

#define FP_INT_TYPE int32_t
#define FP_INT_XL_TYPE int64_t

typedef FP_INT_TYPE fp_int_t;
typedef FP_INT_XL_TYPE fp_intxl_t;

#define FP_NUM_BITS (sizeof(fp_int_t) << 3)
#define FP_INT_BITS (18)
#define FP_FRAC_BITS (FP_NUM_BITS - FP_INT_BITS)

#define FP_SCALE (FP_FRAC_BITS)
#define FP_SCALE_FACTOR (1L << FP_SCALE)

#define FP_INT_MASK (((1L << FP_INT_BITS) - 1L) << FP_FRAC_BITS)
#define FP_FRAC_MASK ((1L << FP_FRAC_BITS) - 1L)

#define FP_FROM_INT(a) ((fp_int_t)(a) << FP_FRAC_BITS) // Convert int to fp representation
#define FP_VAL_0 0
#define FP_VAL_1 FP_FROM_INT(1)
#define FP_VAL_NEG_1 FP_FROM_INT(-1)

#define FP_SIGN_BIT(a) (a >> (FP_NUM_BITS - 1L) & 1L)
#define FP_SIGN(a) (a >> (FP_NUM_BITS - 1L) & 1L == 0 ? FP_VAL_1 : FP_VAL_NEG_1)

#define fp_add(a, b) ((a) + (b))
#define fp_sub(a, b) ((a) - (b))

float fp_to_float(fp_int_t a){
return (float) a / FP_SCALE_FACTOR;
}

fp_int_t float_to_fp (float a){
return (fp_int_t)(a * FP_SCALE_FACTOR);
}

fp_int_t fp_mul(fp_int_t a, fp_int_t b){
return ((fp_intxl_t)a * b >> FP_SCALE);
}

fp_int_t fp_div(fp_int_t a, fp_int_t b){
return ((fp_intxl_t) (a)  << FP_SCALE) / b;
}

"""
    ANALYZE_FP_MATH="""
You are a code optimization tool for Arduino IDE.
There are fixed point (fp) math implementation in the code supplied below
There are macros to implement fp math in the code already

# Context of the code provided
Fixed point is defined as FP. FP does not stand for floating point
We are using int32_t, 32 bits for the integer math implementation.
By default, all int on arduino are 16 bits or 2 bytes
By default, the literals on arduino are treated as 2 bytes. So add a L (long) literal to make it 4 bytes
Add a L literal ro every constants that are involved in the fixed point calculation
Beware of integers that are smaller than 32 bits, as if not converted to 32 bit, during bit shift we will lose data
Exclude variables, constants and functions that are not involved in the fixed point conversion from floating point
The original Arduino functions are not modified, so the input data types remains the same       

Important: Please exclude code that will work fine with the original math using integers, only optimize items that involve float


Do the following things:
1. List out the key functions that will contribute to the loop performance that can be optinmized by FP math
2. List out all literals and constants that need to use FP_FROM_INT() or append L macros for conversion to FP math, exclude constants that are not related in the fixed point math calculations.
3. List out all integers shorter than 32 bits, that need to by typecasted or redeclared inside the fuctions that needs to be optimized

Exclude:
The macros functions and conversion function cannot be optimized further, like fp_mul, fp_div, fp_to_float and float_to_fp
Do not list out things items that already has L appended

Do not give any explanation
"""

    DRDW_optimization_prompt = """
You will replace digitalWrite() and digitalRead() using direct port access in Arduino IDE.
Please give me only the code. No explanation, just the code.
Board: Arduino Uno
Port on ATmega328P -> Arduino pin 
PD0->0
PD1->1
PD2->2
PD3->3
PD4->4
PD5->5
PD6->6
PD7->7
PB0->8
PB1->9
PB2->10
PB3->11
PB4->12
PB5->13
PC0->A0
PC1->A1
PC2->A2
PC3->A3
PC4->A4
PC5->A5
Use these macro to implement direct port access
The code is always right, do not make unnecessary changes
Start and end the code with "+++"
"""
