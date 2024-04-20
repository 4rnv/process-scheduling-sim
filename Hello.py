import streamlit as st
import pandas as pd
import altair as alt
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

def run():
    st.set_page_config(
        page_title="Process Scheduling Simulator",
        page_icon="🆘",
        initial_sidebar_state="collapsed",
        menu_items={
        'Report a bug': "https://github.com/4rnv/process-scheduling-sim/issues",
        'About': "Nothing really."
        }
    )
    st.markdown(
    """
    <style>
    [data-testid="collapsedControl"] {
        display: none
    }
    </style>
    """, 
    unsafe_allow_html=True,
    )
    
    st.write("# Process Scheduling Simulator")
    st.subheader("😴😴😴")
    st.markdown(
        """
        Enter the arrival and burst times of your processes
    """
    )
    with st.form("Formdesu"):
      scheduler_type = st.selectbox('Select an algorithm',('FCFS (First Come First Serve)', 'SJF (Shortest Job First)', 'SRTF (Shortest Remaining Time First)'))
      arrival_times = st.text_input(label="Enter arrival times separated by a single space (no commas)", placeholder="2 4 6 8 10")
      burst_times = st.text_input(label="Enter burst times separated by a single space (no commas)", placeholder="2 4 6 8 10")
      state = st.form_submit_button("Solve", type="primary")
      if state:
            arrival_times_list = list(map(int, arrival_times.split()))
            burst_times_list = list(map(int, burst_times.split()))
            labels = [f'Process {i+1}' for i in range(len(arrival_times_list))]
            if len(arrival_times_list) != len(burst_times_list):
                st.warning("Amount of the arrival times and burst times do not match")
            else:
                if scheduler_type == "FCFS (First Come First Serve)":
                    start_times, completion_times, wait_times, turnaround_times = fcfs(arrival_times_list, burst_times_list)
                elif scheduler_type == "SJF (Shortest Job First)":
                    start_times, completion_times, wait_times, turnaround_times = sjf(arrival_times_list, burst_times_list)
                elif scheduler_type == "SRTF (Shortest Remaining Time First)":
                    start_times, completion_times, wait_times, turnaround_times = srtf(arrival_times_list, burst_times_list)
                create_table(start_times, completion_times, wait_times, turnaround_times, labels)
                plot_gantt_chart(scheduler_type, start_times, burst_times_list, labels)
                avg_tat = float(sum(turnaround_times))/len(turnaround_times)
                avg_wt = float(sum(wait_times))/len(wait_times)
                st.write("Average Turn Around Time is {avg_tat} units".format(avg_tat = avg_tat))
                st.write("Average Waiting Time is {avg_wt} units".format(avg_wt = avg_wt))


def fcfs(arrival_times, burst_times):
    start_times = [0] * len(arrival_times)
    completion_times = [0] * len(arrival_times)
    wait_times = [0] * len(arrival_times)
    turnaround_times = [0] * len(arrival_times)
    
    for i in range(len(arrival_times)):
        if i == 0:
            start_times[i] = arrival_times[i]
        else:
            start_times[i] = max(completion_times[i-1], arrival_times[i])
        completion_times[i] = start_times[i] + burst_times[i]
        turnaround_times[i] = completion_times[i] - arrival_times[i]
        wait_times[i] = turnaround_times[i] - burst_times[i]
    
    return start_times, completion_times, wait_times, turnaround_times
  
def sjf(arrival_times, burst_times):
    n = len(arrival_times)
    completion_times = [0] * n
    wait_times = [0] * n
    turnaround_times = [0] * n
    start_times = [0] * n
    remaining_burst_times = burst_times[:]
    is_completed = [False] * n
    current_time = 0
    completed = 0
    
    while completed != n:
        idx = -1
        min_burst = float('inf')
        for i in range(n):
            if arrival_times[i] <= current_time and not is_completed[i] and remaining_burst_times[i] < min_burst:
                min_burst = remaining_burst_times[i]
                idx = i
        if idx != -1:
            start_times[idx] = current_time
            completion_times[idx] = current_time + burst_times[idx]
            wait_times[idx] = current_time - arrival_times[idx]
            turnaround_times[idx] = completion_times[idx] - arrival_times[idx]
            is_completed[idx] = True
            current_time += burst_times[idx]
            completed += 1
        else:
            current_time += 1
    
    return start_times, completion_times, wait_times, turnaround_times

def srtf(arrival_times, burst_times):
    n = len(arrival_times)
    completion_times = [0] * n
    wait_times = [0] * n
    turnaround_times = [0] * n
    start_times = [-1] * n
    remaining_burst_times = burst_times[:]
    is_completed = [False] * n
    current_time = 0
    completed = 0
    last_idx = -1
    
    while completed != n:
        idx = -1
        min_burst = float('inf')
        for i in range(n):
            if arrival_times[i] <= current_time and not is_completed[i] and remaining_burst_times[i] < min_burst:
                min_burst = remaining_burst_times[i]
                idx = i
        if idx != -1:
            if last_idx != idx and start_times[idx] == -1:
                start_times[idx] = current_time
            elif last_idx != idx:
                start_times[idx] = current_time
            remaining_burst_times[idx] -= 1
            if remaining_burst_times[idx] == 0:
                completion_times[idx] = current_time + 1
                wait_times[idx] = completion_times[idx] - arrival_times[idx] - burst_times[idx]
                turnaround_times[idx] = completion_times[idx] - arrival_times[idx]
                is_completed[idx] = True
                completed += 1
            last_idx = idx
        current_time += 1
    
    # Adjust start times for those that were preempted
    for i in range(n):
        if start_times[i] == -1:
            start_times[i] = arrival_times[i]
    
    return start_times, completion_times, wait_times, turnaround_times

def plot_gantt_chart(scheduler_type, start_times, burst_times, labels):
    # Create a DataFrame for the Gantt chart
    df = pd.DataFrame({
        'Task': labels,
        'Start': start_times,
        'Finish': [start + burst for start, burst in zip(start_times, burst_times)],
        'Duration': burst_times
    })

    # Create a chart
    chart = alt.Chart(df).mark_bar().encode(
        x='Start:Q',
        x2='Finish:Q',
        y=alt.Y('Task:N', sort=list(df['Task']), title='Process ID'),
        tooltip=['Task', 'Start', 'Finish', 'Duration']
    ).properties(
        title=f"Gantt Chart for {scheduler_type}"
    )

    st.altair_chart(chart, use_container_width=True)

def create_table(start_times, completion_times, wait_times, turnaround_times, labels):
    table_df = pd.DataFrame({
        "Process Name" : labels,
        "Start" : start_times,
        "Completion Time" : completion_times,
        "Turn Around Time" : turnaround_times,
        "Wait Time" : wait_times,
    })
    st.dataframe(table_df, use_container_width=True, hide_index=True)
if __name__ == "__main__":
    run()
