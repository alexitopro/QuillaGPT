import streamlit as st
from streamlit_extras.stylable_container import stylable_container

# Include Font Awesome CSS
st.markdown(
    '<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons"/>',
    unsafe_allow_html=True,
)

parte_2 = st.container()
with parte_2:
    # Custom CSS to style the first button and remove its border
    with stylable_container(
        key="container_with_border",
        css_styles=r"""
            .element-container:has(#button-after) + div button {
                border: none;
                background: none;
                padding: 0;
                cursor: pointer;
                font-family: 'Material Icons';
                font-size: 50px;
            }
            .element-container:has(#button-after) + div button::before {
                content: 'add_circle';
                display: inline-block;
                padding-right: 3px;
                vertical-align: middle;
                font-weight: 900;
            }
            """,
    ):
        st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
        if st.button(''):
            st.write('Button clicked!')

parte_1 = st.container()
with parte_1:
    # Regular button
    st.button("Click me")