import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Router, NavigationExtras  } from '@angular/router';
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

  constructor(private http: HttpClient, private router: Router) { }

  ngOnInit(): void {
    this.loadFamilies();
  }

  loadFamilies(): void {
    this.http.get(environment.apiUrl + '/articles/families')
      .subscribe((data) => {
        this.families = this.families.concat(data);
        this.loading = false;
      });
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

  showFamily(nomfam: string, codfam: number): void {
    if (this.router.url !== '/family') {
      const navigationExtras: NavigationExtras = {
        queryParams: {'nomfam': nomfam, 'codfam': codfam }
      };

      this.router.navigate(['/family'], navigationExtras);;
    }
  }

}
