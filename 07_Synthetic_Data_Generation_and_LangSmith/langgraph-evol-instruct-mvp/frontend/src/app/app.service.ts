import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

export interface UploadResponse {
  message: string;
  result_id: string;
  task_id: string;
  total_documents: number;
  evolved_questions_count: number;
  validation_metrics: any;
}

export interface ProcessingResults {
  evolved_questions: any[];
  answers: any[];
  contexts: any[];
  validation_metrics: any;
}

export interface AgentStep {
  step_id: number;
  timestamp: string;
  agent_type?: string;
  status: string;
  details: string;
  agent_message?: string;
  question_preview?: string;
  context_preview?: string;
  error?: string;
}

export interface ProgressUpdate {
  task_id: string;
  status: string;
  step: string;
  step_number: number;
  total_steps: number;
  percentage: number;
  details: string;
  timestamp: string;
  files_count?: number;
  result_id?: string;
  agent_steps?: AgentStep[];
  total_agent_steps?: number;
}

@Injectable({
  providedIn: 'root'
})
export class AppService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { 
    console.log('API URL configured for:', this.apiUrl);
  }

  setApiKey(apiKey: string): Observable<any> {
    const formData = new FormData();
    formData.append('api_key', apiKey);
    return this.http.post(`${this.apiUrl}/set-api-key`, formData);
  }

  getApiKeyStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/api-key-status`);
  }

  uploadDocuments(files: File[], apiKey?: string): Observable<UploadResponse> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    if (apiKey) {
      formData.append('api_key', apiKey);
    }
    return this.http.post<UploadResponse>(`${this.apiUrl}/upload`, formData);
  }

  getResults(resultId: string): Observable<ProcessingResults> {
    return this.http.get<ProcessingResults>(`${this.apiUrl}/results/${resultId}`);
  }

  getProgress(taskId: string): Observable<ProgressUpdate> {
    return this.http.get<ProgressUpdate>(`${this.apiUrl}/progress/${taskId}`);
  }

  listResults(): Observable<any> {
    return this.http.get(`${this.apiUrl}/results`);
  }

  healthCheck(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health`);
  }
} 