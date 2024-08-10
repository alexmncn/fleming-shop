import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-search-bar',
  standalone: true,
  imports: [],
  templateUrl: './search-bar.component.html',
  styleUrl: './search-bar.component.css'
})
export class SearchBarComponent implements OnInit {
  totalArticlesURL: string = environment.apiUrl + '/articles/total';
  totalArticles: any = 'todos los'; 

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.getTotalArticles();
  }

  getTotalArticles(): void {
    this.http.get<any>(this.totalArticlesURL)
      .subscribe((data) => {
        this.totalArticles = data.total;
      });
  }

  get placeholder(): string {
    return 'Buscar entre ' + this.totalArticles + ' artículos';
  }
}
