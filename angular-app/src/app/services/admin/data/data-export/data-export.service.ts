import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { environment } from '../../../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DataExportService {
  private baseUrl = environment.apiUrl;
  private articlesExportUrl = this.baseUrl + '/data/export/articles';
  private familiesExportUrl = this.baseUrl + '/data/export/families';
  private cierresExportUrl = this.baseUrl + '/data/export/cierres';
  private movimientosExportUrl = this.baseUrl + '/data/export/movimientos'
  private ticketsExportUrl = this.baseUrl + '/data/export/tickets'


  constructor(private http: HttpClient) { }

  getArticlesFile(format: string) {
    return this.http.get(this.articlesExportUrl, { params: { "format": format }, responseType: 'blob' });
  }

  getFamiliesFile(format: string) {
    return this.http.get(this.familiesExportUrl, { params: { "format": format }, responseType: 'blob' });
  }

  getCierresFile(format: string) {
    return this.http.get(this.cierresExportUrl, { params: { "format": format }, responseType: 'blob' });
  }

  getMovimientosFile(format: string) {
    return this.http.get(this.movimientosExportUrl, { params: { "format": format }, responseType: 'blob' });
  }
  getTicketsFile(format: string) {
    return this.http.get(this.ticketsExportUrl, { params: { "format": format }, responseType: 'blob' });
  }
}
