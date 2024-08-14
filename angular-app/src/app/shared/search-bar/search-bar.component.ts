import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router, NavigationExtras } from '@angular/router';

import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-search-bar',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './search-bar.component.html',
  styleUrl: './search-bar.component.css'
})
export class SearchBarComponent implements OnInit {
  @Output() search = new EventEmitter<string>();
  searchParam: string = '';

  totalArticlesURL: string = environment.apiUrl + '/articles/total';
  totalArticles: any = 'todos los'; 

  constructor(private http: HttpClient, private router: Router) { }

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

  onSearch(): void {
    if (this.router.url !== '/search') {
      const navigationExtras: NavigationExtras = {
        queryParams: { 'q': this.searchParam }
      };

      this.router.navigate(['/search'], navigationExtras);;
    } else {
      this.search.emit(this.searchParam);
    }
  }
}
