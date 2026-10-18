import matplotlib.pyplot as plt
import networkx as nx
from typing import List, Dict
import os

class DiagramGenerator:
    """Utility for generating agent interaction diagrams"""
    
    @staticmethod
    def generate_mermaid_diagram() -> str:
        """Generate Mermaid diagram showing agent interactions
        
        Returns:
            Mermaid diagram code
        """
        mermaid_code = """
graph TD
    A[JD Summarizer Agent] -->|Passes JD summaries| C[Matching Agent]
    B[CV Extractor Agent] -->|Passes parsed CVs| C
    C -->|Passes match scores| D[Shortlisting Agent]
    D -->|Passes shortlisted candidates| E[Interview Scheduler Agent]
    
    classDef agent fill:#f9f,stroke:#333,stroke-width:2px;
    class A,B,C,D,E agent;
    """
        
        return mermaid_code
    
    @staticmethod
    def generate_matplotlib_diagram(output_file: str = "agent_diagram.png") -> str:
        """Generate diagram showing agent interactions using matplotlib
        
        Args:
            output_file: Path to save the diagram
            
        Returns:
            Path to the generated diagram
        """
        # Create directed graph
        G = nx.DiGraph()
        
        # Add nodes (agents)
        agents = [
            "JD Summarizer Agent",
            "CV Extractor Agent",
            "Matching Agent",
            "Shortlisting Agent",
            "Interview Scheduler Agent"
        ]
        
        for agent in agents:
            G.add_node(agent)
        
        # Add edges (interactions)
        interactions = [
            ("JD Summarizer Agent", "Matching Agent", "Passes JD summaries"),
            ("CV Extractor Agent", "Matching Agent", "Passes parsed CVs"),
            ("Matching Agent", "Shortlisting Agent", "Passes match scores"),
            ("Shortlisting Agent", "Interview Scheduler Agent", "Passes shortlisted candidates")
        ]
        
        for source, target, label in interactions:
            G.add_edge(source, target, label=label)
        
        # Set up the plot
        plt.figure(figsize=(12, 8))
        pos = {
            "JD Summarizer Agent": (-1, 0),
            "CV Extractor Agent": (1, 0),
            "Matching Agent": (0, -1),
            "Shortlisting Agent": (0, -2),
            "Interview Scheduler Agent": (0, -3)
        }
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='lightblue', alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, width=2, alpha=0.5, edge_color='gray', 
                               arrowsize=20, arrows=True, connectionstyle='arc3,rad=0.1')
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
        
        # Draw edge labels
        edge_labels = {(source, target): label for source, target, label in interactions}
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        
        # Set title
        plt.title("Agent Interaction Diagram", size=15)
        
        # Remove axis
        plt.axis('off')
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_file
    
    @staticmethod
    def save_mermaid_diagram(output_file: str = "agent_diagram.md") -> str:
        """Save Mermaid diagram to file
        
        Args:
            output_file: Path to save the diagram
            
        Returns:
            Path to the generated diagram file
        """
        mermaid_code = DiagramGenerator.generate_mermaid_diagram()
        
        # Wrap in markdown code block
        content = f"# Agent Interaction Diagram\n\n```mermaid\n{mermaid_code}\n```"
        
        # Save to file
        with open(output_file, 'w') as f:
            f.write(content)
        
        return output_file 