import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { AppService, UploadResponse, ProcessingResults, ProgressUpdate } from './app.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = 'LangGraph Evol Instruct MVP';
  
  selectedFiles: File[] = [];
  isUploading = false;
  uploadResponse: UploadResponse | null = null;
  processingResults: ProcessingResults | null = null;
  errorMessage = '';
  
  // API Key management
  apiKey = '';
  hasApiKey = false;
  isSettingApiKey = false;
  isCheckingApiKey = true;

  // Progress tracking
  currentProgress: ProgressUpdate | null = null;
  progressInterval: any = null;
  currentTaskId: string | null = null;

  constructor(private appService: AppService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
    this.checkApiKeyStatus();
  }

  checkApiKeyStatus() {
    this.isCheckingApiKey = true;
    this.appService.getApiKeyStatus().subscribe({
      next: (response) => {
        this.hasApiKey = response.has_api_key;
        this.isCheckingApiKey = false;
        console.log('API key status:', response);
      },
      error: (error) => {
        console.error('Failed to check API key status:', error);
        this.hasApiKey = false; // Default to showing API key input
        this.isCheckingApiKey = false;
      }
    });
  }

  setApiKey() {
    if (!this.apiKey.trim()) {
      this.errorMessage = 'Please enter an API key';
      return;
    }

    this.isSettingApiKey = true;
    this.errorMessage = '';

    this.appService.setApiKey(this.apiKey).subscribe({
      next: (response) => {
        this.hasApiKey = true;
        this.isSettingApiKey = false;
        this.errorMessage = '';
        console.log('API key set successfully:', response);
      },
      error: (error) => {
        this.errorMessage = `Failed to set API key: ${error.message}`;
        this.isSettingApiKey = false;
        console.error('Error setting API key:', error);
      }
    });
  }

  onFileSelected(event: any): void {
    this.selectedFiles = Array.from(event.target.files);
    this.errorMessage = '';
  }

  uploadFiles(): void {
    if (this.selectedFiles.length === 0) {
      this.errorMessage = 'Please select files to upload';
      return;
    }

    if (!this.hasApiKey && !this.apiKey.trim()) {
      this.errorMessage = 'Please set an API key first';
      return;
    }

    this.isUploading = true;
    this.errorMessage = '';
    this.currentProgress = null;
    console.log('Starting file upload...');

    // Use stored API key or the one in the input field
    const apiKeyToUse = this.hasApiKey ? undefined : this.apiKey;

    this.appService.uploadDocuments(this.selectedFiles, apiKeyToUse).subscribe({
      next: (response) => {
        console.log('Upload response received:', response);
        this.uploadResponse = response;
        this.isUploading = false;
        this.cdr.detectChanges(); // Force UI update
        
        // Start progress tracking
        if (response.task_id) {
          console.log('Task ID received:', response.task_id);
          this.startProgressTracking(response.task_id);
        } else {
          console.warn('No task_id in response');
        }
      },
      error: (error) => {
        console.error('Upload error:', error);
        this.errorMessage = `Upload failed: ${error.message}`;
        this.isUploading = false;
        this.stopProgressTracking();
      }
    });
  }

  loadResults(resultId: string): void {
    console.log('Loading results for resultId:', resultId);
    this.appService.getResults(resultId).subscribe({
      next: (results) => {
        console.log('Results loaded successfully:', results);
        this.processingResults = results;
        this.cdr.detectChanges(); // Force UI update
      },
      error: (error) => {
        console.error('Error loading results:', error);
        this.errorMessage = `Failed to load results: ${error.message}`;
      }
    });
  }

  getAnswerForQuestion(questionId: string): string {
    if (!this.processingResults) return '';
    const answer = this.processingResults.answers.find(a => a.question_id === questionId);
    return answer ? answer.answer : 'No answer available';
  }

  getContextForQuestion(questionId: string): string {
    if (!this.processingResults) return '';
    const context = this.processingResults.contexts.find(c => c.question_id === questionId);
    return context ? context.context : 'No context available';
  }

  startProgressTracking(taskId: string): void {
    console.log('Starting progress tracking for task:', taskId);
    this.currentTaskId = taskId;
    this.progressInterval = setInterval(() => {
      console.log('Polling progress for task:', taskId);
      this.appService.getProgress(taskId).subscribe({
        next: (progress) => {
          console.log('Progress update received:', progress);
          this.currentProgress = progress;
          this.cdr.detectChanges(); // Force UI update
          
          // Stop tracking if completed or error
          if (progress.status === 'completed' || progress.status === 'error') {
            console.log('Progress completed/error, stopping tracking');
            console.log('Progress status:', progress.status);
            console.log('Result ID:', progress.result_id);
            this.stopProgressTracking();
            
            if (progress.status === 'completed' && progress.result_id) {
              console.log('Loading results for:', progress.result_id);
              this.loadResults(progress.result_id);
            } else {
              console.log('No result_id found or status not completed');
            }
          }
        },
        error: (error) => {
          console.error('Error fetching progress:', error);
        }
      });
    }, 500); // Poll every 500ms for more responsive updates
  }

  stopProgressTracking(): void {
    if (this.progressInterval) {
      clearInterval(this.progressInterval);
      this.progressInterval = null;
    }
    this.currentTaskId = null;
  }

  // 🤖 Helper methods for agent step display
  getAgentTypeIcon(agentType: string): string {
    const icons: {[key: string]: string} = {
      'simple': '🤖',
      'multi_context': '🔄', 
      'reasoning': '🧩',
      'answer_generator': '🧠',
      'validation': '🔍',
      'orchestrator': '🎭',
      'document': '📄',
      'question': '🤔'
    };
    return icons[agentType] || '⚙️';
  }

  getStatusIcon(status: string): string {
    const statusIcons: {[key: string]: string} = {
      'initializing': '🟡',
      'processing': '🔄',
      'analyzing': '🔍', 
      'consolidating': '🎯',
      'summarizing': '📝',
      'completed': '✅',
      'fallback': '⚠️',
      'error': '❌'
    };
    return statusIcons[status] || '⚪';
  }

  formatTime(timestamp: string): string {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  }

} 