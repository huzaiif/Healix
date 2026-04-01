import streamlit as st
from database.db import get_reports, delete_report

def show_reports():
    st.title("Saved Reports 📑")
    st.markdown("View all your saved health assessments and reports.")
    
    user_id = st.session_state['user_id']
    
    reports = get_reports(user_id)
    
    if not reports:
        st.info("No saved reports found. Run a disease prediction assessment to save one!")
        return
        
    for report in reports:
        with st.expander(f"{report['title']} - {report['created_at'][:10]}"):
            st.markdown(f"**Date:** {report['created_at']}")
            st.markdown(report['content'])
            col1, col2 = st.columns([1, 1])
            with col1:
                from utils.pdf_generator import generate_simple_pdf
                pdf_buffer = generate_simple_pdf(report['title'], report['content'])
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_buffer,
                    file_name=f"health_report_{report['id']}.pdf",
                    mime="application/pdf",
                    key=f"dl_report_{report['id']}",
                    use_container_width=True
                )
            with col2:
                if st.button("Delete Report", key=f"del_report_{report['id']}", use_container_width=True):
                    delete_report(report['id'], user_id)
                    st.success("Report deleted.")
                    st.rerun()

if __name__ == "__main__":
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        show_reports()
    else:
        st.warning("Please log in to view this page.")
