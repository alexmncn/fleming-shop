import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { catchError, timeout } from 'rxjs/operators';
import { of, throwError } from 'rxjs';
import { ArticlesService } from '../../services/catalog/articles/articles.service';

import { ArticlesComponent } from "../../shared/articles/articles.component";

@Component({
    selector: 'app-family',
    imports: [CommonModule, ArticlesComponent],
    templateUrl: './family.component.html',
    styleUrl: './family.component.css'
})
export class FamilyComponent {
  nomfam: string = '';
  codfam: number = 0;
  articles: any[] = [];
  totalArticles: number = 0;
  perPage: number = 30;
  articlesPage: number = 1;
  articlesOrderBy: string = 'detalle';
  articlesDirection: string = 'asc';
  loadingArticles: boolean = false;
  statusCode: number = -1;

  constructor(private route: ActivatedRoute, private articlesService: ArticlesService) { }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.nomfam = params['nomfam'];
      this.codfam = params['codfam'];
      if (this.nomfam) {
        this.loadTotalFamilyArticles();
        this.loadFamilyArticles();
      }
    });
  }

  loadTotalFamilyArticles(): void {
    this.articlesService.getTotalFamilyArticles(this.codfam).subscribe({
      next: (res) => this.totalArticles = res.total,
      error: (err) => {
        this.statusCode = err.status || 500;
        console.error('Error fetching total:', err);
      }
    });
  }

  loadFamilyArticles(): void {
    this.loadingArticles = true;
    this.articlesService.getFamilyArticles(this.codfam, this.articlesPage, this.perPage, this.articlesOrderBy, this.articlesDirection)
      .pipe(
        timeout(10000),
        catchError(err => {
          this.loadingArticles = false;
          this.statusCode = err.status || 500;
          return of([]);
        })
      )
      .subscribe({
        next: (articles) => {
          this.articles = [...this.articles, ...articles];
          this.articlesPage++;
          this.loadingArticles = false;
        },
        error: (err) => {
          this.loadingArticles = false;
          this.statusCode = err.status;
        }
      });
  }

  onSortChangeArticles(order_by: string, direction: string): void {
    this.articlesOrderBy = order_by;
    this.articlesDirection = direction;
    this.articlesPage = 1;
    this.articles = [];
    this.loadFamilyArticles();
  }
}