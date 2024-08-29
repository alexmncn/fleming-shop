import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router, NavigationExtras } from '@angular/router';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { InputTextModule } from 'primeng/inputtext';

import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-search-bar',
  standalone: true,
  imports: [FormsModule, IconFieldModule, InputIconModule, InputTextModule],
  templateUrl: './search-bar.component.html',
  styleUrl: './search-bar.component.css'
})
export class SearchBarComponent implements OnInit {
  @Output() search = new EventEmitter<string>();
  @Output() isFocused = new EventEmitter<boolean>();
  searchParam: string = '';
  isInputFocused: boolean = false;

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
    this.onBlur();
    if (this.router.url !== '/search') {
      const navigationExtras: NavigationExtras = {
        queryParams: { 'q': this.searchParam }
      };

      this.router.navigate(['/search'], navigationExtras);;
    } else {
      this.search.emit(this.searchParam);
    }
  }

  onFocus(): void {
    this.isInputFocused = true;
    this.isFocused.emit(this.isInputFocused);
  }

  onBlur(): void {
    this.isInputFocused = false;
    this.isFocused.emit(this.isInputFocused);
  }
}
