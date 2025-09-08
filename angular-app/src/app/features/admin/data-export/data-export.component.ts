import { Component } from '@angular/core';

import { DataExportService } from '../../../services/admin/data/data-export/data-export.service';
import { MessageService } from '../../../services/message/message.service';

@Component({
  selector: 'app-data-export',
  imports: [],
  templateUrl: './data-export.component.html',
  styleUrl: './data-export.component.css'
})
export class DataExportComponent {
  formatOptions = [
    { value: 'csv', viewValue: 'CSV', icon: 'pi pi-file-o' },
    { value: 'xlsx', viewValue: 'EXCEL', icon: 'pi pi-file-excel' },
    { value: 'pdf', viewValue: 'PDF', icon: 'pi pi-file-pdf' },
    { value: 'dbf', viewValue: 'DBF', icon: 'pi pi-database' }
  ];

  isDownloading: boolean = false;
  lastFile: string = '';
  lastFormat: string = '';

  constructor(private dataExportService: DataExportService, private messageService: MessageService) {}

  private fileServiceMap: { [key: string]: (format: string) => any } = {
    articles: (format) => this.dataExportService.getArticlesFile(format),
    families: (format) => this.dataExportService.getFamiliesFile(format),
    cierres: (format) => this.dataExportService.getCierresFile(format),
    movimientos: (format) => this.dataExportService.getMovimientosFile(format),
    tickets: (format) => this.dataExportService.getTicketsFile(format),
  };

  downloadFile(filename: string, format: string) {
    const serviceFn = this.fileServiceMap[filename];
    if (!serviceFn) return;

    this.lastFile = filename;
    this.lastFormat = format;
    this.isDownloading = true;

    serviceFn(format).subscribe({
      next: (file: Blob) => {
      const url = window.URL.createObjectURL(file);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${filename}.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
      this.isDownloading = false;
      this.messageService.showMessage('success', 'Archivo descargado correctamente', 5);
      },
      error: (err: any) => {
        this.isDownloading = false;
        if (err?.status === 404) {
          this.messageService.showMessage('warn', 'No existen datos o archivo para descargar');
        } else {
          console.error('Error al descargar el archivo:', err);
          this.messageService.showMessage('error', 'Error al descargar el archivo');
        }
      }
    });
  }
}
