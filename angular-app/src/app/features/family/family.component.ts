import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { catchError, timeout } from 'rxjs/operators';
import { of, throwError } from 'rxjs';

import { environment } from '../../../environments/environment';

import { ArticlesComponent } from "../../shared/articles/articles.component";

@Component({
  selector: 'app-family',
  standalone: true,
  imports: [CommonModule, ArticlesComponent],
  templateUrl: './family.component.html',
  styleUrl: './family.component.css'
})
export class FamilyComponent {
  familiesURL: string = environment.apiUrl + '/articles/families'
  nomfam: string = '';
  codfam: number = 0;
  articles: any[] = [];
  totalArticles: number = 0;
  per_page: number = 30;
  articlesPage: number = 1;
  loadingArticles: boolean = false;
  statusCode: number = -1;

  constructor(private http: HttpClient, private route: ActivatedRoute) { }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.nomfam = params['nomfam'];
      this.codfam = params['codfam'];
      if (this.nomfam) {
        this.getTotalFamilyArticles();
        this.loadFamilyArticles();
      }
    });
  }

  getTotalFamilyArticles(): void {
    this.http.get<any>(this.familiesURL + '/' + this.codfam + '/total')
      .subscribe((data) => {
        this.totalArticles = data.total;
      });
  }

  loadFamilyArticles(): void {
    this.loadingArticles = true;
    this.http.get(this.familiesURL + '/' + this.codfam, {params: {'page': this.articlesPage, 'per_page': this.per_page}})
      .pipe(
        timeout(10000),
        catchError(error => {
          this.loadingArticles = false;
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
        next: (response) => {
          this.articles = this.articles.concat(response);
          this.articlesPage++;
        
          this.loadingArticles = false;
        },
        error: (error) => {
          this.loadingArticles = false;
          this.statusCode = error.status;
        },
        complete: () => {
        }
      });
  }
}