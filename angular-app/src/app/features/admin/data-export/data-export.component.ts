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

  downloadFile(filename: string, format: string) {
    if (filename === 'articles') {
      this.lastFile = filename;
      this.lastFormat = format;
      this.isDownloading = true;
      
      this.dataExportService.getArticlesFile(format).subscribe({
        next: (file: Blob) => {
          const url = window.URL.createObjectURL(file);
          const a = document.createElement('a');
          a.href = url;
          a.download = `articles.${format}`;
          a.click();
          window.URL.revokeObjectURL(url);
          this.isDownloading = false;
          this.messageService.showMessage('success', 'Archivo descargado correctamente', 5);
        },
        error: (err) => {
          console.error('Error al descargar el archivo:', err);
          this.isDownloading = false;
          this.messageService.showMessage('error', 'Error al descargar el archivo');
        }
      });
    } else if (filename === 'families' ) {
      this.lastFile = filename;
      this.lastFormat = format;
      this.isDownloading = true;
      
      this.dataExportService.getFamiliesFile(format).subscribe({
        next: (file: Blob) => {
          const url = window.URL.createObjectURL(file);
          const a = document.createElement('a');
          a.href = url;
          a.download = `families.${format}`;
          a.click();
          window.URL.revokeObjectURL(url);
          this.isDownloading = false;
          this.messageService.showMessage('success', 'Archivo descargado correctamente', 5);
        },
        error: (err) => {
          console.error('Error al descargar el archivo:', err);
          this.isDownloading = false;
          this.messageService.showMessage('error', 'Error al descargar el archivo');
        }
      });
    } else if (filename === 'cierres' ) {
      this.lastFile = filename;
      this.lastFormat = format;
      this.isDownloading = true;
      
      this.dataExportService.getCierresFile(format).subscribe({
        next: (file: Blob) => {
          const url = window.URL.createObjectURL(file);
          const a = document.createElement('a');
          a.href = url;
          a.download = `cierres.${format}`;
          a.click();
          window.URL.revokeObjectURL(url);
          this.isDownloading = false;
          this.messageService.showMessage('success', 'Archivo descargado correctamente', 5);
        },
        error: (err) => {
          console.error('Error al descargar el archivo:', err);
          this.isDownloading = false;
          this.messageService.showMessage('error', 'Error al descargar el archivo');
        }
      });
    } else if (filename === 'movimientos' ) {
      this.lastFile = filename;
      this.lastFormat = format;
      this.isDownloading = true;
      
      this.dataExportService.getMovimientosFile(format).subscribe({
        next: (file: Blob) => {
          const url = window.URL.createObjectURL(file);
          const a = document.createElement('a');
          a.href = url;
          a.download = `movimientos.${format}`;
          a.click();
          window.URL.revokeObjectURL(url);
          this.isDownloading = false;
          this.messageService.showMessage('success', 'Archivo descargado correctamente', 5);
        },
        error: (err) => {
          console.error('Error al descargar el archivo:', err);
          this.isDownloading = false;
          this.messageService.showMessage('error', 'Error al descargar el archivo');
        }
      });
    } else if (filename === 'tickets' ) {
      this.lastFile = filename;
      this.lastFormat = format;
      this.isDownloading = true;
      
      this.dataExportService.getTicketsFile(format).subscribe({
        next: (file: Blob) => {
          const url = window.URL.createObjectURL(file);
          const a = document.createElement('a');
          a.href = url;
          a.download = `tickets.${format}`;
          a.click();
          window.URL.revokeObjectURL(url);
          this.isDownloading = false;
          this.messageService.showMessage('success', 'Archivo descargado correctamente', 5);
        },
        error: (err) => {
          console.error('Error al descargar el archivo:', err);
          this.isDownloading = false;
          this.messageService.showMessage('error', 'Error al descargar el archivo');
        }
      });
    }
  }
}
