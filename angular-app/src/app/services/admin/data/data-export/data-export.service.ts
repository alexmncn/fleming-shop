import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { environment } from '../../../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DataExportService {
  private baseUrl = environment.apiUrl;
  private articleExportUrl = this.baseUrl + '/data/export/articles';


  constructor(private http: HttpClient) { }

  getArticlesFile(format: string) {
    return this.http.get(this.articleExportUrl + '.' + format, { responseType: 'blob' });
  }
}
