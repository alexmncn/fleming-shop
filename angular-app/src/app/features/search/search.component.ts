import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';

import { environment } from '../../../environments/environment';

import { SearchBarComponent } from "../../shared/search-bar/search-bar.component";
import { ArticlesComponent } from "../../shared/articles/articles.component";

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [CommonModule, SearchBarComponent, ArticlesComponent],
  templateUrl: './search.component.html',
  styleUrl: './search.component.css'
})
export class SearchComponent {
  searchURL: string = environment.apiUrl + '/articles/search';
  articles: any[] = [];
  totalArticles: number = 0;
  per_page: number = 30;
  searchParam: string = '';
  lastSearchParam: string = 'none';
  articlesPage: number = 1;
  loadingArticles: boolean = false;


  constructor(private http: HttpClient, private route: ActivatedRoute) { }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.searchParam = params['q'] || '';
      if (this.searchParam) {
        this.onSearch(this.searchParam);
      }
    });
  }

  getTotalSearchArticles(): void {
    this.http.get<any>(this.searchURL + '/total', {params: {'search': this.searchParam}})
      .subscribe((data) => {
        this.totalArticles = data.total;
      });
  }

  onSearch(param: string = ''): void {
    this.loadingArticles = true;
    this.searchParam = param;
    if (this.searchParam === this.lastSearchParam) {
      this.http.get(this.searchURL, {params: {'search': this.searchParam, 'page': this.articlesPage, 'per_page': this.per_page}})
      .subscribe((data) => {
        this.articles = this.articles.concat(data);
        this.articlesPage++;
        this.lastSearchParam = this.searchParam;

        this.loadingArticles = false;
      });
    } else {
      this.articlesPage = 1;
      this.articles = [];
      this.getTotalSearchArticles();
      this.http.get(this.searchURL, {params: {'search': this.searchParam, 'page': this.articlesPage, 'per_page': this.per_page}})
        .subscribe((data) => {
          this.articles = this.articles.concat(data);
          this.articlesPage++;
          this.lastSearchParam = this.searchParam;
          
          this.loadingArticles = false;
        });
    }
  }

}
