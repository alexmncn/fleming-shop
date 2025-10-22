import { Component, effect, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, NavigationExtras } from '@angular/router';
import { SkeletonModule } from 'primeng/skeleton';
import { trigger, style, transition, animate, state } from '@angular/animations';

import { CapitalizePipe } from '../../pipes/capitalize/capitalize-pipe';

import { CatalogStoreService } from '../../services/catalog/catalog-store.service';

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
  families = this.catalogStore.families.families;
  total = this.catalogStore.families.total;
  loading = this.catalogStore.families.loading;
  statusCode = this.catalogStore.families.statusCode;

  placeholders = signal<string[]>(new Array(20).fill(''));
  familiesUnfold: boolean = false;

  constructor(private catalogStore: CatalogStoreService, private router: Router) {}

  ngOnInit(): void {
    if (this.catalogStore.families.families().length === 0) {
      this.catalogStore.families.loadTotal();
      this.catalogStore.families.load();
    }
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
    return this.statusCode() == 404 && this.families.length == 0 && !this.loading;
  }

  get serverError(): boolean {
    return (this.statusCode() == 408 || this.statusCode.toString().startsWith('5')) && this.families.length == 0 && !this.loading;
  }

}
