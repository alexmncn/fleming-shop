import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Router, NavigationExtras } from '@angular/router';
import { SkeletonModule } from 'primeng/skeleton';
import { trigger, style, transition, animate, state } from '@angular/animations';

import { CapitalizePipe } from '../../pipes/capitalize/capitalize-pipe';

import { environment } from '../../../environments/environment';
import { catchError, of, throwError, timeout } from 'rxjs';

@Component({
    selector: 'app-families',
    imports: [CommonModule, SkeletonModule, CapitalizePipe],
    templateUrl: './families.component.html',
    styleUrl: './families.component.css',
    animations: [
        trigger('arrowRotateLeft', [
            state('void', style({
                transform: 'rotate(180deg)',
            })),
            transition(':enter', [
                animate('0.25s ease-out', style({
                    transform: 'rotate(0deg)',
                }))
            ]),
            transition(':leave', [
                animate('0s ease-in', style({
                    opacity: 0
                }))
            ])
        ]),
        trigger('arrowRotateRight', [
            state('void', style({
                transform: 'rotate(-180deg)',
            })),
            transition(':enter', [
                animate('0.25s ease-out', style({
                    transform: 'rotate(0deg)',
                }))
            ]),
            transition(':leave', [
                animate('0s ease-in', style({
                    opacity: 0
                }))
            ])
        ])
    ]
})
export class FamiliesComponent implements OnInit {
  families: any[] = [];
  placeholders: any[] = new Array(20).fill('');
  loading: boolean = true;
  familiesUnfold: boolean = false;
  statusCode: number = -1;

  constructor(private http: HttpClient, private router: Router) { }

  ngOnInit(): void {
    this.loadFamilies();
  }

  loadFamilies(): void {
    this.http.get(environment.apiUrl + '/articles/families')
      .pipe(
        timeout(10000),
        catchError(error => {
          this.loading = false;
          if (error.name === 'TimeoutError') {
            console.error('Request timed out');
            this.statusCode = 408;
            return of([]);
          }
          const status = error.status || 500;
          const message = error.message || 'An unknown error occurred';

          return throwError(() => ({
            status,
            message
          }));
        })
      )
      .subscribe({
        next:(response) => {
          this.families = this.families.concat(response);
          this.loading = false;  
        },
        error: (error) => {
          this.loading = false;
          this.statusCode = error.status;
        },
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
    this.familiesUnfold = !this.familiesUnfold;
  }

  showFamily(nomfam: string, codfam: number): void {
    if (this.router.url !== '/catalog/family') {
      const navigationExtras: NavigationExtras = {
        queryParams: {'nomfam': nomfam, 'codfam': codfam }
      };

      this.router.navigate(['/catalog/family'], navigationExtras);;
    }
  }

  get noFamilies(): boolean {
    return this.statusCode == 404 && this.families.length == 0 && !this.loading;
  }

  get serverError(): boolean {
    return (this.statusCode == 408 || this.statusCode.toString().startsWith('5')) && this.families.length == 0 && !this.loading;
  }

}
