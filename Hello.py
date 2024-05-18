import streamlit as st
import pandas as pd
import altair as alt
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

def run():
    st.set_page_config(
        page_title="Process Scheduling Simulator",
        page_icon="🌸",
        initial_sidebar_state="collapsed",
        menu_items={
        'Report a bug': "https://github.com/4rnv/process-scheduling-sim/issues",
        'About': "Project by : Arnav Dandekar, Samarth Bhandavale, Pushkar Uikey, Siddhesh Goenka",
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
    st.subheader("Operating Systems")
    st.markdown(
        """
        Enter the arrival and burst times of your processes. This program will calculate the execution times for each process.
        You can also download the Gantt chart and table after generation.
    """
    )

    scheduler_type = st.selectbox(
        'Select an algorithm',
        ('FCFS (First Come First Serve)', 'SJF (Shortest Job First)', 
         'SRTF (Shortest Remaining Time First)', 'RR (Round Robin)',
         'Priority (Non -Preemptive)')
    )

    with st.form("OHSHC"):
      arrival_times = st.text_input(
            label="Enter arrival times separated by a single space (no commas)", 
            placeholder="2 4 6 8 10"
        )
      burst_times = st.text_input(
            label="Enter burst times separated by a single space (no commas)", 
            placeholder="2 4 6 8 10"
        )
      if scheduler_type == "RR (Round Robin)":
            quantum_time = st.text_input(label="Enter Quantum", placeholder="0")
      if scheduler_type == "Priority (Non -Preemptive)":
            priority_order = st.text_input(label="Enter Priority", placeholder="High Value High Priority")
      state = st.form_submit_button("Solve", type="primary")
      if state:
        st.write("Scheduler Type:", scheduler_type)
        if scheduler_type == "RR (Round Robin)":
            st.write("Quantum Time:", quantum_time)
        if len(arrival_times) != 0 and len(burst_times) != 0:
            try:
                flag = 1
                arrival_times_list = list(map(int, arrival_times.split()))
                burst_times_list = list(map(int, burst_times.split()))
                labels = [f'Process {i+1}' for i in range(len(arrival_times_list))]
                data = list(zip(labels, arrival_times_list, burst_times_list))
                if scheduler_type == "Priority (Non -Preemptive)":
                    priority_order_list = list(map(int, priority_order.split()))
                if len(arrival_times_list) != len(burst_times_list):
                    st.warning("Amount of the arrival times and burst times do not match")
                else:
                    if scheduler_type == "FCFS (First Come First Serve)":
                        start_times, completion_times, wait_times, turnaround_times = shinfcfs(data)
                    elif scheduler_type == "SJF (Shortest Job First)":
                        start_times, completion_times, wait_times, turnaround_times = sjf(arrival_times_list, burst_times_list)
                    elif scheduler_type == "SRTF (Shortest Remaining Time First)":
                        start_times, completion_times, wait_times, turnaround_times = srtf(arrival_times_list, burst_times_list)
                    elif scheduler_type == "RR (Round Robin)":
                        if quantum_time:
                            try:
                                quantum_time = int(quantum_time)
                                start_times, completion_times, wait_times, turnaround_times = rr(data, quantum_time)
                            except:
                                st.error("Quantum time can only be an integer number")
                                flag = 0
                    elif scheduler_type == "Priority (Non -Preemptive)":
                        if priority_order_list:
                            try:
                                data,start_times, completion_times, wait_times, turnaround_times = priority(arrival_times_list,burst_times_list,priority_order_list)
                            except:
                                st.error("Invalid Input")
                                flag = 0
                    if flag == 1:
                        create_table(start_times, completion_times, wait_times, turnaround_times, data)
                        plot_gantt_chart(scheduler_type, start_times, data)
                        avg_tat = float(sum(turnaround_times))/len(turnaround_times)
                        avg_wt = float(sum(wait_times))/len(wait_times)
                        st.write("Average Turn Around Time is {avg_tat} units".format(avg_tat = avg_tat))
                        st.write("Average Waiting Time is {avg_wt} units".format(avg_wt = avg_wt))
            except ValueError:
                st.error("Only integers are allowed", icon="🙄")
        else:
            st.warning("Your input is empty")

def shinfcfs(data):
    data.sort(key=lambda x: x[1])
    start_times = []
    completion_times = []
    wait_times = []
    turnaround_times = []
    last_completion_time = 0

    for i in range(len(data)):
        process_name, arrival_time, burst_time = data[i]
        if last_completion_time < arrival_time:
            start_time = arrival_time
        else:
            start_time = last_completion_time
        start_times.append(start_time)
        completion_time = start_time + burst_time
        completion_times.append(completion_time)
        last_completion_time = completion_time
        turnaround_time = completion_time - arrival_time
        turnaround_times.append(turnaround_time)
        wait_time = start_time - arrival_time
        wait_times.append(wait_time)

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

    for i in range(n):
        if start_times[i] == -1:
            start_times[i] = arrival_times[i]

    return start_times, completion_times, wait_times, turnaround_times

def rr(data, quantum):
    if quantum <=0:
        st.error("Time cannot be negative or zero", icon="💅")
    data.sort(key=lambda x: x[1])
    n = len(data)
    remaining_burst_times = [x[2] for x in data]  # Initial burst times
    arrival_times = [x[1] for x in data]
    start_times = [-1] * n  # To record the first time a process is picked up
    completion_times = [0] * n
    t = 0
    queue = []
    process_index = 0

    while True:
        while process_index < n and arrival_times[process_index] <= t:
            if process_index not in queue:
                queue.append(process_index)
            process_index += 1

        if not queue:
            if process_index < n:
                t = arrival_times[process_index]
            else:
                break
        if queue:
            current_process = queue.pop(0)
            if start_times[current_process] == -1:
                start_times[current_process] = t
            
            service_time = min(quantum, remaining_burst_times[current_process])
            remaining_burst_times[current_process] -= service_time
            t += service_time

            if remaining_burst_times[current_process] == 0:
                completion_times[current_process] = t
            else:
                while process_index < n and arrival_times[process_index] <= t:
                    if process_index not in queue:
                        queue.append(process_index)
                    process_index += 1
                queue.append(current_process)

    wait_times = [0] * n
    turnaround_times = [0] * n
    for i in range(n):
        turnaround_times[i] = completion_times[i] - arrival_times[i]
        wait_times[i] = turnaround_times[i] - data[i][2]

    return start_times, completion_times, wait_times, turnaround_times

def priority(arrival_time, burst_time, p):
    p_id = [i + 1 for i in range(len(arrival_time))]
    process = {p_id[i]: [arrival_time[i], burst_time[i], p[i]] for i in range(len(arrival_time))}
    process = dict(sorted(process.items(), key=lambda item: item[1][2], reverse=True))
    start = 0
    gantt = {}
    for i in range(len(process)):
        for j in process:
            if process[j][0] <= start and j not in gantt:
                gantt[j] = [start,start+process[j][1]]
                start = start+process[j][1]
                break
    start_times = [gantt[i][0] for i in gantt]
    completion_times = [gantt[i][1] for i in gantt]
    arrival_times = [process[i][0] for i in process]
    burst_times = [process[i][1] for i in process]
    p_id = [i for i in process]
    turnaround_times = [completion_times[i] - arrival_times[i] for i in range(len(process))]
    wait_times = [turnaround_times[i] - burst_times[i] for i in range(len(process))]
    data = list(zip(p_id, arrival_times, burst_times))
    return data,start_times, completion_times, wait_times, turnaround_times

def plot_gantt_chart(scheduler_type, start_times, data):
    burst_times = [x[2] for x in data]
    labels = [x[0] for x in data]
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

def create_table(start_times, completion_times, wait_times, turnaround_times, data):
    labels = [x[0] for x in data]
    arrival_times_list = [x[1] for x in data]
    burst_times_list = [x[2] for x in data]
    table_df = pd.DataFrame({
        "Process Name" : labels,
        "Arrival Times" : arrival_times_list,
        "I/O Time" : burst_times_list,
        "Start" : start_times,
        "Finish Time" : completion_times,
        "Turn Around Time" : turnaround_times,
        "Wait Time" : wait_times,
    })
    st.dataframe(table_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    run()
