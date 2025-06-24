import os
import streamlit as st
from graphviz import Digraph
import xmltodict
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import json
import re

# ---- Configuration ----
st.set_page_config(
    page_title="LLM-Powered BPM Lifecycle Demo", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- OpenAI Setup ----
def init_llm(api_key, model="gpt-4"):
    """Initialize LLM instance with user-provided API key"""
    if not api_key:
        return None
    
    try:
        return ChatOpenAI(
            openai_api_key=api_key,
            model_name=model,
            temperature=0.1,  # Slightly increased for more creative solutions
            max_retries=3,
            streaming=False
        )
    except Exception as e:
        st.error(f"Error initializing OpenAI API: {str(e)}")
        return None

# ---- Enhanced Helper Functions ----
def extract_tasks_from_text(text):
    """Extract numbered or bulleted tasks from LLM response"""
    # Try to find numbered lists first
    numbered_pattern = r'^\d+\.\s*(.+)$'
    bulleted_pattern = r'^[-•*]\s*(.+)$'
    
    lines = text.strip().split('\n')
    tasks = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for numbered items
        match = re.match(numbered_pattern, line)
        if match:
            tasks.append(match.group(1).strip())
            continue
            
        # Check for bulleted items
        match = re.match(bulleted_pattern, line)
        if match:
            tasks.append(match.group(1).strip())
            continue
            
        # If no pattern matches but line is substantial, include it
        if len(line) > 10 and not line.startswith(('The', 'This', 'Here', 'Below')):
            tasks.append(line)
    
    return tasks if tasks else [line.strip() for line in text.split('\n') if line.strip()]

def generate_enhanced_bpmn_xml(tasks, process_name="Business Process"):
    """Generate more structured BPMN XML with proper elements"""
    if not tasks:
        return ""
    
    # Create start and end events
    elements = []
    flows = []
    
    # Start event
    elements.append({
        'tag': 'startEvent',
        'attrs': {'id': 'StartEvent_1', 'name': 'Start'}
    })
    
    # Tasks
    for i, task in enumerate(tasks):
        task_id = f"Task_{i+1}"
        elements.append({
            'tag': 'task',
            'attrs': {'id': task_id, 'name': task[:50] + ('...' if len(task) > 50 else '')}
        })
    
    # End event
    elements.append({
        'tag': 'endEvent',
        'attrs': {'id': 'EndEvent_1', 'name': 'End'}
    })
    
    # Create sequence flows
    prev_id = 'StartEvent_1'
    for i, task in enumerate(tasks):
        task_id = f"Task_{i+1}"
        flow_id = f"Flow_{i+1}"
        flows.append({
            'id': flow_id,
            'sourceRef': prev_id,
            'targetRef': task_id
        })
        prev_id = task_id
    
    # Final flow to end
    flows.append({
        'id': f"Flow_{len(tasks)+1}",
        'sourceRef': prev_id,
        'targetRef': 'EndEvent_1'
    })
    
    # Build XML structure
    process_dict = {
        'definitions': {
            '@xmlns': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
            '@xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            '@targetNamespace': 'http://bpmn.io/schema/bpmn',
            'process': {
                '@id': 'Process_1',
                '@isExecutable': 'true',
                '@name': process_name
            }
        }
    }
    
    # Add elements to process
    for element in elements:
        tag = element['tag']
        if tag not in process_dict['definitions']['process']:
            process_dict['definitions']['process'][tag] = []
        process_dict['definitions']['process'][tag].append(element['attrs'])
    
    # Add sequence flows
    process_dict['definitions']['process']['sequenceFlow'] = []
    for flow in flows:
        process_dict['definitions']['process']['sequenceFlow'].append({
            '@id': flow['id'],
            '@sourceRef': flow['sourceRef'],
            '@targetRef': flow['targetRef']
        })
    
    return xmltodict.unparse(process_dict, pretty=True)

def create_enhanced_graph(tasks, title="Process Flow"):
    """Create enhanced Graphviz diagram"""
    dot = Digraph(comment=title)
    dot.attr(rankdir='LR', size='12,8')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
    
    # Start node
    dot.node('start', 'START', shape='circle', fillcolor='lightgreen')
    
    # Task nodes
    prev_node = 'start'
    for i, task in enumerate(tasks):
        node_id = f'task_{i}'
        # Truncate long task names for better visualization
        display_name = task[:30] + '...' if len(task) > 30 else task
        dot.node(node_id, display_name)
        dot.edge(prev_node, node_id)
        prev_node = node_id
    
    # End node
    dot.node('end', 'END', shape='circle', fillcolor='lightcoral')
    if tasks:
        dot.edge(prev_node, 'end')
    
    return dot

# ---- Enhanced BPM Stage Templates ----
class BPMStageTemplates:
    
    @staticmethod
    def identification_prompt():
        return ChatPromptTemplate.from_template(
            """As a Business Process Management expert, analyze this business process description:

            {description}

            Provide a comprehensive analysis covering:
            1. **Business Purpose**: What is the core objective of this process?
            2. **Key Stakeholders**: Who are the main participants and beneficiaries?
            3. **Current Pain Points**: What inefficiencies, bottlenecks, or problems do you identify?
            4. **Business Value**: What value does this process deliver to the organization?
            5. **Improvement Potential**: What are the key areas for optimization?

            Keep your response structured and professional."""
        )
    
    @staticmethod
    def discovery_prompt():
        return ChatPromptTemplate.from_template(
            """As a Business Process Analyst, break down this process into clear, sequential steps:

            {description}

            Requirements:
            - Extract the main tasks/activities in chronological order
            - Use clear, action-oriented language
            - Include decision points where applicable
            - Focus on "what" is done, not "how"
            - Number each step for clarity

            Format your response as a numbered list of process steps."""
        )
    
    @staticmethod
    def analysis_prompt():
        return ChatPromptTemplate.from_template(
            """As a Process Improvement Consultant, analyze these process steps for optimization opportunities:

            {steps}

            Provide analysis on:
            1. **Bottlenecks**: Which steps cause delays or capacity constraints?
            2. **Redundancies**: Are there duplicate or unnecessary activities?
            3. **Risk Points**: Where are the highest risks of errors or failures?
            4. **Automation Opportunities**: Which steps could be automated?
            5. **Resource Utilization**: Are resources being used efficiently?
            6. **Quality Issues**: Where might quality problems occur?

            Be specific and actionable in your recommendations."""
        )
    
    @staticmethod
    def redesign_prompt():
        return ChatPromptTemplate.from_template(
            """As a Digital Transformation Specialist, redesign this process to be more efficient:

            Original Process Steps:
            {steps}

            Analysis Findings:
            {analysis}

            Create an optimized process that:
            - Eliminates waste and redundancy
            - Introduces automation where beneficial
            - Improves parallel processing opportunities
            - Reduces handoffs and delays
            - Enhances quality and consistency

            Provide the redesigned process as a numbered list of steps, followed by a brief explanation of key improvements made."""
        )
    
    @staticmethod
    def monitoring_prompt():
        return ChatPromptTemplate.from_template(
            """As a Process Excellence Manager, design a monitoring and optimization framework for this redesigned process:

            Redesigned Process:
            {redesigned_process}

            Provide:
            1. **Key Performance Indicators (KPIs)**: 5-7 metrics to track process performance
            2. **Target Values**: Specific targets for each KPI
            3. **Alert Thresholds**: When to trigger alerts or interventions
            4. **Monitoring Frequency**: How often to measure each KPI
            5. **Continuous Improvement**: Suggestions for ongoing optimization
            6. **Technology Enablers**: Tools or systems that could support monitoring

            Focus on measurable, actionable metrics that drive business value."""
        )

# ---- Enhanced Scenarios ----
DEMO_SCENARIOS = {
    
    "📦 Supply Chain Procurement": {
        "description": """The procurement team identifies a need for materials or services and creates a purchase requisition. The requisition is reviewed and approved by the appropriate manager based on budget and authority levels. Suppliers are identified and requests for quotations are sent out. Supplier responses are evaluated based on price, quality, delivery time, and other criteria. A purchase order is created and sent to the selected supplier. The supplier confirms the order and provides delivery schedules. Goods are received and inspected for quality and quantity. Invoices are processed and payment is made according to agreed terms.""",
        "complexity": "Simple",
        "industry": "Manufacturing"
    },

    "🏪 R&D new product or improvement to an existing one": {
        "description": """The process starts with identifying an idea for a new product or improvement to an
existing one . The R&D team conducts initial research and feasibility studies ,
followed by drafting design concepts . After selecting a promising design , a
prototype is built using available materials and resources . The prototype
undergoes various tests to assess its functionality , safety , and market potential .
Feedback from the testing phase is collected , and the prototype may be refined
accordingly . If a refinement is needed , then the testing phase is reinitiated . The
process ends when the prototype is either approved for further development or
discarded .""",
        "complexity": "Medium",
        "industry": "Manufacturing"
    },
    
    "🏦 University enrollment system": {
        "description": """A university enrollment system involves the following steps :
Prospective students submit an application online .
The admissions office reviews the application and supporting documents .
If documents are missing , the applicant is notified to provide the missing items .
Upon receiving all documents , the application is evaluated by the admissions
committee .
Concurrently , the finance department processes any application fees or waivers .
If the application is accepted , an acceptance letter is sent . Otherwise , a
rejection letter is sent and the process ends .
After being accepted , the student must then confirm enrollment by a specified
deadline ; otherwise the application will be canceled .
If the student confirms , they receive orientation materials and the IT department
sets up student accounts for email , online portals , and library access .
If the student is international , the international student office assists with visa
processing .
The student obtains a student ID card and starts creating their study plan , which
includes :
Meeting with an academic advisor .
Selecting courses .
Resolving any schedule conflicts .
The student begins attending classes .
Throughout each semester , the student may add or drop courses within the add / drop
period .
At the end of the semester , grades are posted , and the student can review them
online .
If the student has any grievances , they can file an appeal , which includes :
Submitting an appeal form .
Meeting with the appeals committee .
Awaiting a decision .
The process repeats each semester until the student graduates or withdraws .""",
        "complexity": "Complex",
        "industry": "Education"
    }
}

# ---- Main Application ----
def main():
    st.title("🚀 LLM for BPM Lifecycle")
    st.markdown("""
    This application demonstrates the potential of Large Language Models in Business Process Management (BPM) 
    across all five key stages of the BPM lifecycle - with zero-shot learning and no custom training.
    """)
    
    # API Key input section
    st.info("🔑 **Please provide your OpenAI API key to use this application**")
    
    # Create columns for better layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        api_key = st.text_input(
            "Enter your OpenAI API Key:",
            type="password",
            placeholder="sk-...",
            help="Your API key is not stored and is only used for this session. Get your API key from https://platform.openai.com/api-keys"
        )
    
    with col2:
        model_choice = st.selectbox(
            "Select Model:",
            ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            help="GPT-4 provides better analysis but costs more"
        )
    
    if not api_key:
        st.warning("⚠️ Please enter your OpenAI API key to continue.")
        st.markdown("""
        **How to get your OpenAI API key:**
        1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
        2. Sign in to your account (or create one)
        3. Click "Create new secret key"
        4. Copy the key and paste it above
        
        **Note**: Your API key is only used for this session and is not stored anywhere.
        """)
        return
    
    # Initialize LLM
    llm = init_llm(api_key, model_choice)
    if not llm:
        st.error("Failed to initialize OpenAI API. Please check your API key.")
        return
    
    st.success(f"✅ Successfully connected to OpenAI API using {model_choice}")
    st.divider()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Select Scenario")
        
        # Scenario selection
        scenario_choice = st.selectbox(
            "Select Business Process Scenario",
            ["Custom Input"] + list(DEMO_SCENARIOS.keys())
        )
        
        # Advanced options
        show_xml = st.checkbox("Show BPMN XML", False)
        show_prompts = st.checkbox("Show Prompts", False)
        
        st.divider()
        st.markdown("**💡 Tips:**")
        st.markdown("- Use detailed process descriptions for better results")
        st.markdown("- GPT-4 provides more comprehensive analysis")
        st.markdown("- Download BPMN files to use in process modeling tools")

    # Process input
    if scenario_choice == "Custom Input":
        process_description = st.text_area(
            "📝 Enter your business process description:",
            height=200,
            placeholder="Describe your business process in detail..."
        )
        process_name = st.text_input("Process Name", "Custom Business Process")
    else:
        scenario = DEMO_SCENARIOS[scenario_choice]
        process_description = st.text_area(
            f"📝 Process Description ({scenario['complexity']} - {scenario['industry']}):",
            value=scenario['description'],
            height=200
        )
        process_name = scenario_choice
    
    # Analysis button
    if st.button("🔍 Run Complete BPM Analysis", type="primary"):
        if not process_description.strip():
            st.error("Please provide a process description!")
            return
        
        # Initialize stage templates
        templates = BPMStageTemplates()
        
        # Create tabs for each stage
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "1️⃣ Identification", 
            "2️⃣ Discovery", 
            "3️⃣ Analysis", 
            "4️⃣ Redesign", 
            "5️⃣ Monitoring"
        ])
        
        with tab1:
            st.header("🎯 Process Identification")
            st.markdown("*Understanding the business context and value proposition*")
            
            with st.spinner("Analyzing business context..."):
                try:
                    identification_chain = LLMChain(llm=llm, prompt=templates.identification_prompt())
                    if show_prompts:
                        with st.expander("View Prompt"):
                            st.code(templates.identification_prompt().template)
                    
                    identification_result = identification_chain.run(description=process_description)
                    st.markdown(identification_result)
                except Exception as e:
                    st.error(f"Error in identification stage: {str(e)}")
        
        with tab2:
            st.header("🔍 Process Discovery")
            st.markdown("*Mapping out the current state process flow*")
            
            with st.spinner("Discovering process steps..."):
                try:
                    discovery_chain = LLMChain(llm=llm, prompt=templates.discovery_prompt())
                    if show_prompts:
                        with st.expander("View Prompt"):
                            st.code(templates.discovery_prompt().template)
                    
                    discovery_result = discovery_chain.run(description=process_description)
                    
                    # Extract tasks for visualization
                    current_tasks = extract_tasks_from_text(discovery_result)
                    
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.subheader("Process Steps")
                        st.markdown(discovery_result)
                    
                    with col2:
                        st.subheader("As-Is Process Flow")
                        if current_tasks:
                            current_graph = create_enhanced_graph(current_tasks, "Current Process")
                            st.graphviz_chart(current_graph)
                            
                            # BPMN XML download
                            current_xml = generate_enhanced_bpmn_xml(current_tasks, f"{process_name} - As-Is")
                            st.download_button(
                                "📄 Download As-Is BPMN",
                                current_xml,
                                file_name=f"{process_name.lower().replace(' ', '_')}_as_is.bpmn",
                                mime="application/xml"
                            )
                            
                            if show_xml:
                                with st.expander("View BPMN XML"):
                                    st.code(current_xml, language="xml")
                except Exception as e:
                    st.error(f"Error in discovery stage: {str(e)}")
        
        with tab3:
            st.header("📊 Process Analysis")
            st.markdown("*Identifying bottlenecks, risks, and improvement opportunities*")
            
            if 'discovery_result' in locals():
                with st.spinner("Analyzing process inefficiencies..."):
                    try:
                        analysis_chain = LLMChain(llm=llm, prompt=templates.analysis_prompt())
                        if show_prompts:
                            with st.expander("View Prompt"):
                                st.code(templates.analysis_prompt().template)
                        
                        analysis_result = analysis_chain.run(steps=discovery_result)
                        st.markdown(analysis_result)
                    except Exception as e:
                        st.error(f"Error in analysis stage: {str(e)}")
            else:
                st.warning("Please complete the Discovery stage first.")
        
        with tab4:
            st.header("🔄 Process Redesign")
            st.markdown("*Creating an optimized future state process*")
            
            if 'analysis_result' in locals():
                with st.spinner("Redesigning process for optimization..."):
                    try:
                        redesign_chain = LLMChain(llm=llm, prompt=templates.redesign_prompt())
                        if show_prompts:
                            with st.expander("View Prompt"):
                                st.code(templates.redesign_prompt().template)
                        
                        redesign_result = redesign_chain.run(
                            steps=discovery_result,
                            analysis=analysis_result
                        )
                        
                        # Extract redesigned tasks
                        redesigned_tasks = extract_tasks_from_text(redesign_result)
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.subheader("Redesigned Process")
                            st.markdown(redesign_result)
                        
                        with col2:
                            st.subheader("To-Be Process Flow")
                            if redesigned_tasks:
                                redesigned_graph = create_enhanced_graph(redesigned_tasks, "Redesigned Process")
                                st.graphviz_chart(redesigned_graph)
                                
                                # BPMN XML download
                                redesigned_xml = generate_enhanced_bpmn_xml(redesigned_tasks, f"{process_name} - To-Be")
                                st.download_button(
                                    "📄 Download To-Be BPMN",
                                    redesigned_xml,
                                    file_name=f"{process_name.lower().replace(' ', '_')}_to_be.bpmn",
                                    mime="application/xml"
                                )
                                
                                if show_xml:
                                    with st.expander("View BPMN XML"):
                                        st.code(redesigned_xml, language="xml")
                    except Exception as e:
                        st.error(f"Error in redesign stage: {str(e)}")
            else:
                st.warning("Please complete the Analysis stage first.")
        
        with tab5:
            st.header("📈 Process Monitoring & Optimization")
            st.markdown("*Establishing KPIs and continuous improvement framework*")
            
            if 'redesign_result' in locals():
                with st.spinner("Designing monitoring framework..."):
                    try:
                        monitoring_chain = LLMChain(llm=llm, prompt=templates.monitoring_prompt())
                        if show_prompts:
                            with st.expander("View Prompt"):
                                st.code(templates.monitoring_prompt().template)
                        
                        monitoring_result = monitoring_chain.run(redesigned_process=redesign_result)
                        st.markdown(monitoring_result)
                    except Exception as e:
                        st.error(f"Error in monitoring stage: {str(e)}")
            else:
                st.warning("Please complete the Redesign stage first.")
        
        st.success("✅ Complete BPM Lifecycle Analysis Generated Successfully!")
        st.balloons()

# ---- Footer ----
def show_footer():
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 14px;'>
    🤖 <strong>LLM in BPM</strong> | Showcasing AI capabilities in Business Process Management<br>
    <em>Your API key is secure and only used for this session</em>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
    show_footer()
