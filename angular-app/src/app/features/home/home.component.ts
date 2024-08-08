import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { MatIcon } from '@angular/material/icon';

import { ArticlesComponent } from '../../shared/articles/articles.component';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, ArticlesComponent, MatIcon],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit {
  families: any[] = [];
  featuredArticles: any[] = [];
  newArticles: any[] = [];

  familiesUnfold: boolean = false;

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.loadFamilies();
    this.loadFeaturedArticles()
    this.loadNewArticles()
  }
  
  loadFamilies(): void {
    this.http.get('http://127.0.0.1:5000/articles/families')
      .subscribe((data) => {
        this.families = this.families.concat(data);
      });
  }

  loadFeaturedArticles(): void {
    setTimeout(() => {
      this.http.get('http://127.0.0.1:5000/articles/featured')
      .subscribe((data) => {
        this.featuredArticles = this.featuredArticles.concat(data);
      });
    }, 2000);
  }

  loadNewArticles(): void {
    setTimeout(() => {
      this.http.get('http://127.0.0.1:5000/articles/new')
      .subscribe((data) => {
        this.newArticles = this.newArticles.concat(data);
      });
    }, 1000);
  }

  onFamilyScroll(event: WheelEvent): void {
    if (!this.familiesUnfold) {
      const scrollContainer = event.currentTarget as HTMLElement;
      if (event.deltaY !== 0) {
        event.preventDefault();
        const scrollAmount = event.deltaY * 2;
        scrollContainer.scrollLeft += scrollAmount;
        
      }
    }
  }

  toggleFamiliesDisplay() {
    if (this.familiesUnfold) {
      this.familiesUnfold = false;
    } else {
      this.familiesUnfold = true;
    }
  }

}
