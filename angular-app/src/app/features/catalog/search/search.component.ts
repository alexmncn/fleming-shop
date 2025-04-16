import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { catchError, timeout } from 'rxjs/operators';
import { of } from 'rxjs';

import { ArticlesComponent } from "../../../shared/articles/articles.component";
import { ArticlesService } from '../../../services/catalog/articles/articles.service';

@Component({
    selector: 'app-search',
    imports: [CommonModule, ArticlesComponent],
    templateUrl: './search.component.html',
    styleUrl: './search.component.css'
})
export class SearchComponent {
  articles: any[] = [];
  totalArticles: number = 0;
  perPage: number = 30;
  articlesPage: number = 1;
  loadingArticles: boolean = false;
  statusCode: number = -1;

  searchParam: string = '';
  lastSearchParam: string = 'none';
  filter: string = 'detalle';
  contextFilter: string = '';
  contextValue: string = '';
  orderBy: string = 'detalle';
  direction: string = 'asc';


  constructor(private articlesService: ArticlesService, private route: ActivatedRoute) { }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.searchParam = params['q'] || '';
      if (this.searchParam) {
        this.onSearch(this.searchParam);
      }
    });
  }

  onSearch(param: string = ''): void {
    if (param !== '') {
      this.loadingArticles = true;
      this.searchParam = param;
      if (this.searchParam === this.lastSearchParam) {
        this.loadSearchArticles();
      } else {
        this.articlesPage = 1;
        this.articles = [];
        this.getTotalSearchArticles();
        this.loadSearchArticles();
      }
    }
  }

  getTotalSearchArticles(): void {
    this.articlesService.getTotalSearchArticles(this.searchParam, this.filter, this.contextFilter, this.contextValue).subscribe({
      next: (res) => this.totalArticles = res.total,
      error: (err) => {
        this.statusCode = err.status || 500;
        console.error('Error fetching total:', err);
      }
    });
  }

  loadSearchArticles(): void {
    this.articlesService.getSearchArticles(this.searchParam, this.filter, this.contextFilter, this.contextValue, this.articlesPage, this.perPage, this.orderBy, this.direction)
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
          this.lastSearchParam = this.searchParam;
          this.loadingArticles = false;
        },
        error: (err) => {
          this.loadingArticles = false;
          this.statusCode = err.status;
        }
      });
  }

  onSortChange(orderBy: string, direction: string): void {
    this.orderBy = orderBy;
    this.direction = direction;
    this.articlesPage = 1;
    this.articles = [];
    this.loadSearchArticles();
  }

}
