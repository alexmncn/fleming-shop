import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { MatIcon } from '@angular/material/icon';
import { SkeletonModule } from 'primeng/skeleton';

import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-families',
  standalone: true,
  imports: [CommonModule, MatIcon, SkeletonModule],
  templateUrl: './families.component.html',
  styleUrl: './families.component.css'
})
export class FamiliesComponent implements OnInit {
  families: any[] = [];
  placeholders: any[] = new Array(20).fill('');
  loading: boolean = true;
  familiesUnfold: boolean = false;

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.loadFamilies();
  }

  loadFamilies(): void {
    setTimeout(() => {
      this.http.get(environment.apiUrl + '/articles/families')
        .subscribe((data) => {
          this.families = this.families.concat(data);
          this.loading = false;
        });
    }, 2000);
  }

  
  onFamilyScroll(event: WheelEvent): void {
    if (!this.familiesUnfold) {
      const scrollContainer = event.currentTarget as HTMLElement;
      if (event.deltaY !== 0) {
        event.preventDefault();
        const scrollAmount = event.deltaY * 2;
        scrollContainer.scrollLeft += scrollAmount;
        
      }
    }
  }

  toggleFamiliesDisplay() {
    if (this.familiesUnfold) {
      this.familiesUnfold = false;
    } else {
      this.familiesUnfold = true;
    }
  }
}
