import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

st.write(os.listdir())
