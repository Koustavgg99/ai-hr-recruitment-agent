import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ReportGenerator:
    """Generate various reports and analytics for HR recruitment"""
    
    def __init__(self, hr_agent):
        self.hr_agent = hr_agent
        self.db = hr_agent.db
    
    def generate_json_report(self, date: str = None) -> str:
        """Generate a structured JSON report"""
        report = self.hr_agent.generate_daily_report(date)
        return json.dumps(report, indent=2, default=str)
    
    def generate_table_report(self, date: str = None) -> pd.DataFrame:
        """Generate a pandas DataFrame report for easy viewing"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Get basic metrics
        metrics = self.db.get_daily_metrics(date)
        pipeline = self.hr_agent.get_pipeline_status()
        
        # Create summary DataFrame
        summary_data = {
            'Metric': [
                'Candidates Sourced Today',
                'Candidates Shortlisted Today',
                'Candidates Contacted Today',
                'Responses Received Today',
                'Active Jobs',
                'Total Candidates in Pipeline',
                'Overall Response Rate'
            ],
            'Value': [
                metrics['candidates_sourced'],
                metrics['candidates_shortlisted'],
                metrics['candidates_contacted'],
                metrics['responses_received'],
                pipeline['active_jobs'],
                pipeline['total_candidates'],
                f"{(pipeline['responded_candidates']/pipeline['contacted_candidates']*100):.1f}%" 
                if pipeline['contacted_candidates'] > 0 else "0%"
            ]
        }
        
        return pd.DataFrame(summary_data)
    
    def generate_candidate_performance_table(self, job_id: int = None) -> pd.DataFrame:
        """Generate candidate performance table"""
        if job_id:
            candidates = self.db.get_candidates_by_job(job_id)
        else:
            # Get all candidates from all jobs
            jobs = self.db.get_jobs()
            candidates = []
            for job in jobs:
                candidates.extend(self.db.get_candidates_by_job(job['id']))
        
        if not candidates:
            return pd.DataFrame()
        
        # Prepare data for DataFrame
        candidate_data = []
        for candidate in candidates:
            candidate_data.append({
                'Name': candidate['name'],
                'Email': candidate['email'],
                'Skills': ', '.join(candidate['skills'][:3]) + ('...' if len(candidate['skills']) > 3 else ''),
                'Experience (Years)': candidate['experience_years'],
                'Location': candidate['location'],
                'Match Score': f"{candidate['match_score']:.2f}",
                'Status': candidate['response_status'].replace('_', ' ').title(),
                'Last Contacted': candidate['last_contacted'] or 'Never'
            })
        
        df = pd.DataFrame(candidate_data)
        return df.sort_values('Match Score', ascending=False)
    
    def generate_weekly_trend_data(self) -> Dict:
        """Generate weekly trend data for visualization"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        trend_data = {
            'dates': [],
            'candidates_sourced': [],
            'candidates_contacted': [],
            'responses_received': []
        }
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            metrics = self.db.get_daily_metrics(date_str)
            
            trend_data['dates'].append(date_str)
            trend_data['candidates_sourced'].append(metrics['candidates_sourced'])
            trend_data['candidates_contacted'].append(metrics['candidates_contacted'])
            trend_data['responses_received'].append(metrics['responses_received'])
            
            current_date += timedelta(days=1)
        
        return trend_data
    
    def create_dashboard_charts(self) -> Dict:
        """Create Plotly charts for dashboard"""
        charts = {}
        
        # 1. Weekly trend chart
        trend_data = self.generate_weekly_trend_data()
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend_data['dates'],
            y=trend_data['candidates_sourced'],
            mode='lines+markers',
            name='Sourced',
            line=dict(color='blue')
        ))
        fig_trend.add_trace(go.Scatter(
            x=trend_data['dates'],
            y=trend_data['candidates_contacted'],
            mode='lines+markers',
            name='Contacted',
            line=dict(color='orange')
        ))
        fig_trend.add_trace(go.Scatter(
            x=trend_data['dates'],
            y=trend_data['responses_received'],
            mode='lines+markers',
            name='Responded',
            line=dict(color='green')
        ))
        
        fig_trend.update_layout(
            title='7-Day Recruitment Trend',
            xaxis_title='Date',
            yaxis_title='Number of Candidates',
            hovermode='x unified'
        )
        charts['trend'] = fig_trend
        
        # 2. Job pipeline status
        pipeline = self.hr_agent.get_pipeline_status()
        
        if pipeline['jobs_detail']:
            job_names = [job['title'] for job in pipeline['jobs_detail']]
            candidate_counts = [job['candidates'] for job in pipeline['jobs_detail']]
            
            fig_pipeline = go.Figure(data=[
                go.Bar(x=job_names, y=candidate_counts, text=candidate_counts, textposition='auto')
            ])
            fig_pipeline.update_layout(
                title='Candidates by Job Position',
                xaxis_title='Job Title',
                yaxis_title='Number of Candidates'
            )
            charts['pipeline'] = fig_pipeline
        
        # 3. Response rate pie chart
        contacted = pipeline['contacted_candidates']
        responded = pipeline['responded_candidates']
        pending = contacted - responded
        
        if contacted > 0:
            fig_response = go.Figure(data=[go.Pie(
                labels=['Responded', 'Pending Response'],
                values=[responded, pending],
                hole=.3
            )])
            fig_response.update_layout(title='Response Rate Overview')
            charts['response_rate'] = fig_response
        
        return charts
    
    def export_candidates_to_csv(self, job_id: int = None, filename: str = None) -> str:
        """Export candidates to CSV file"""
        df = self.generate_candidate_performance_table(job_id)
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            job_suffix = f"_job_{job_id}" if job_id else "_all_jobs"
            filename = f"candidates_export{job_suffix}_{timestamp}.csv"
        
        filepath = f"./data/{filename}"
        df.to_csv(filepath, index=False)
        
        return filepath
    
    def generate_executive_summary(self) -> Dict:
        """Generate high-level executive summary"""
        pipeline = self.hr_agent.get_pipeline_status()
        today_metrics = self.db.get_daily_metrics()
        
        # Calculate key KPIs
        total_candidates = pipeline['total_candidates']
        contacted_candidates = pipeline['contacted_candidates']
        responded_candidates = pipeline['responded_candidates']
        
        response_rate = (responded_candidates / contacted_candidates * 100) if contacted_candidates > 0 else 0
        contact_rate = (contacted_candidates / total_candidates * 100) if total_candidates > 0 else 0
        
        summary = {
            "overview": {
                "active_jobs": pipeline['active_jobs'],
                "total_candidates": total_candidates,
                "response_rate": f"{response_rate:.1f}%",
                "contact_rate": f"{contact_rate:.1f}%"
            },
            "today_performance": {
                "candidates_sourced": today_metrics['candidates_sourced'],
                "candidates_shortlisted": today_metrics['candidates_shortlisted'],
                "outreach_sent": today_metrics['candidates_contacted'],
                "responses_received": today_metrics['responses_received']
            },
            "top_performing_jobs": [],
            "recommendations": []
        }
        
        # Identify top performing jobs
        jobs_with_metrics = []
        for job_detail in pipeline['jobs_detail']:
            if job_detail['candidates'] > 0:
                response_rate = float(job_detail['response_rate'].rstrip('%'))
                jobs_with_metrics.append({
                    'title': job_detail['title'],
                    'candidates': job_detail['candidates'],
                    'response_rate': response_rate
                })
        
        # Sort by response rate and candidate count
        jobs_with_metrics.sort(key=lambda x: (x['response_rate'], x['candidates']), reverse=True)
        summary['top_performing_jobs'] = jobs_with_metrics[:3]
        
        # Generate recommendations
        recommendations = []
        if response_rate < 20:
            recommendations.append("Consider improving outreach message personalization")
        if contact_rate < 50:
            recommendations.append("Increase outreach volume to reach more qualified candidates")
        if today_metrics['candidates_sourced'] == 0:
            recommendations.append("No candidates sourced today - review sourcing strategy")
        
        summary['recommendations'] = recommendations
        
        return summary
