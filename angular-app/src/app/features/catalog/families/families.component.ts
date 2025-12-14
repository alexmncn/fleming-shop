import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { SkeletonModule } from 'primeng/skeleton';

import { CapitalizePipe } from '../../../pipes/capitalize/capitalize-pipe';

import { CatalogStoreService } from '../../../services/catalog/catalog-store.service';
import { Family } from '../../../models/family.model';

@Component({
  selector: 'app-families',
  imports: [CommonModule, SkeletonModule, CapitalizePipe],
  templateUrl: './families.component.html',
  styleUrl: './families.component.css'
})
export class FamiliesComponent implements OnInit {
  families = this.catalogStore.families.families;
  total = this.catalogStore.families.total;
  loading = this.catalogStore.families.loading;
  statusCode = this.catalogStore.families.statusCode;

  placeholders = signal<string[]>(new Array(20).fill(''));

  constructor(private catalogStore: CatalogStoreService, private router: Router) {}

  ngOnInit(): void {
    if (this.catalogStore.families.families().length === 0) {
      this.catalogStore.families.loadTotal();
      this.catalogStore.families.load();
    }
  }

  navigateToFamily(family: Family): void {
    const slug = family.nomfam.toLowerCase().replace(/\s+/g, '-');
    this.router.navigate(['/catalog/family', `${family.codfam}-${slug}`]);
  }

  get noFamilies(): boolean {
    return this.statusCode() == 404 && this.families.length == 0 && !this.loading();
  }

  get serverError(): boolean {
    return (this.statusCode() == 408 || this.statusCode().toString().startsWith('5')) && this.families.length == 0 && !this.loading();
  }
}
