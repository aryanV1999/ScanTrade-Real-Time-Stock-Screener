
import streamlit as st

def calculate_pivot_levels(data):
    high = data['high'].iloc[-1]
    low = data['low'].iloc[-1]
    close = data['close'].iloc[-1]


    #st.write("Previous Day's Data:")
    #st.write(f"High: {high:.2f}")
    #st.write(f"Low: {low:.2f}")
    #st.write(f"Close: {close:.2f}")
    #st.write("---")

    # High Low Difference Calculation
    difference = (high - low)

    # Resistance levels
    r1 = close + 1.1 * (difference) / 12
    r2 = close + 1.1 * (difference) / 6
    r3 = close + 1.1 * (difference) / 4
    r4 = close + 1.1 * (difference) / 2
    r5 = (high/low) * close
    # Support levels
    s1 = close - 1.1 * (difference) / 12
    s2 = close - 1.1 * (difference) / 6
    s3 = close - 1.1 * (difference) / 4
    s4 = close - 1.1 * (difference) / 2
    s5 = close - (r5-close)

    # Print the values (This will be deleted when the project is complete)
    # Print the values
    #st.write("Pivot Levels:")
    #st.write(f"R5: {r5:.2f}")
    #st.write(f"R4: {r4:.2f}")
    #st.write(f"R3: {r3:.2f}")
    #st.write(f"R2: {r2:.2f}")
    #st.write(f"R1: {r1:.2f}")
    #st.write(f"S1: {s1:.2f}")
    #st.write(f"S2: {s2:.2f}")
    #st.write(f"S3: {s3:.2f}")
    #st.write(f"S4: {s4:.2f}")
    #st.write(f"S5: {s5:.2f}")
 
    
    return {
        'r1': float(r1), 'r2': float(r2), 'r3': float(r3), 'r4': float(r4), 'r5': float(r5),
        's1': float(s1), 's2': float(s2), 's3': float(s3), 's4': float(s4), 's5': float(s5)
    }

'''
    PP = (HIGHprev + LOWprev + CLOSEprev) / 3
    R1 = CLOSEprev + 1.1 * (HIGHprev - LOWprev) / 12
    S1 = CLOSEprev - 1.1 * (HIGHprev - LOWprev) / 12
    R2 = CLOSEprev + 1.1 * (HIGHprev - LOWprev) / 6
    S2 = CLOSEprev - 1.1 * (HIGHprev - LOWprev) / 6
    R3 = CLOSEprev + 1.1 * (HIGHprev - LOWprev) / 4
    S3 = CLOSEprev - 1.1 * (HIGHprev - LOWprev) / 4
    R4 = CLOSEprev + 1.1 * (HIGHprev - LOWprev) / 2
    S4 = CLOSEprev - 1.1 * (HIGHprev - LOWprev) / 2
    R5 = (HIGHprev / LOWprev) * CLOSEprev
    S5 = CLOSEprev - (R5 - CLOSEprev)'''