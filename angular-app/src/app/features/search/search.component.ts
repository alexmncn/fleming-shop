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
  per_page: number = 0;
  searchURL: string = environment.apiUrl + '/articles';
  articles: any[] = [];
  searchParam: string = '';


  constructor(private http: HttpClient, private route: ActivatedRoute) { }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.searchParam = params['q'] || '';
      if (this.searchParam) {
        this.onSearch(this.searchParam)
      }
    });
  }

  onSearch(param: string): void {
    this.searchParam = param;
    this.articles = [];
    this.http.get(this.searchURL, {params: {'search': this.searchParam}})
      .subscribe((data) => {
        this.articles = this.articles.concat(data);
      });
  }

}
