import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

import { environment } from '../../../environments/environment';

import { ArticlesComponent } from '../../shared/articles/articles.component';
import { FamiliesComponent } from "../../shared/families/families.component";
import { SearchBarComponent } from "../../shared/search-bar/search-bar.component";

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, ArticlesComponent, FamiliesComponent, SearchBarComponent],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit {
  per_page: number = 20;

  featuredArticlesURL: string = environment.apiUrl + '/articles/featured';
  featuredArticles: any[] = [];
  featuredArticlesPage: number = 1;
  totalFeaturedArticles: number = 0;
  loadingFeaturedArticles: boolean = false;

  newArticlesURL: string = environment.apiUrl + '/articles/new';
  newArticles: any[] = [];
  newArticlesPage: number = 1;
  totalNewArticles: number = 0;
  loadingNewArticles: boolean = false;

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.getTotalFeaturedArticles()
    this.getTotalNewArticles()

    this.loadFeaturedArticles()
    this.loadNewArticles()
  }

  getTotalFeaturedArticles(): void {
    this.http.get<any>(this.featuredArticlesURL + '/total')
      .subscribe((data) => {
        this.totalFeaturedArticles = data.total;
      });
  }

  loadFeaturedArticles(): void {
    this.loadingFeaturedArticles = true;
    this.http.get(this.featuredArticlesURL, {params: {'page': this.featuredArticlesPage, 'per_page': this.per_page}})
    .subscribe((data) => {
      this.featuredArticles = this.featuredArticles.concat(data);
      this.featuredArticlesPage++;

      this.loadingFeaturedArticles = false;
    });
  }
  
  getTotalNewArticles(): void {
    this.http.get<any>(this.newArticlesURL + '/total')
      .subscribe((data) => {
        this.totalNewArticles = data.total;
      });
  }

  loadNewArticles(): void {
  this.loadingNewArticles = true;
    this.http.get(this.newArticlesURL, {params: {'page': this.newArticlesPage, 'per_page': this.per_page}})
    .subscribe((data) => {
      this.newArticles = this.newArticles.concat(data);
      this.newArticlesPage++;

      this.loadingNewArticles = false;
    });
  }
}