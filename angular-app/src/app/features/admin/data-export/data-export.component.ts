import { Component } from '@angular/core';

@Component({
  selector: 'app-data-export',
  imports: [],
  templateUrl: './data-export.component.html',
  styleUrl: './data-export.component.css'
})
export class DataExportComponent {
  formatOptions = [
    { value: 'pdf', viewValue: 'PDF', icon: 'pi pi-file-pdf' },
    { value: 'csv', viewValue: 'CSV', icon: 'pi pi-file-o' },
    { value: 'xlsx', viewValue: 'EXCEL', icon: 'pi pi-file-excel' },
    { value: 'dbf', viewValue: 'DBF', icon: 'pi pi-database' }
  ];

  downloadFile() {

  }
}
