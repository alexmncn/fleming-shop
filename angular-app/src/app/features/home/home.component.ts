import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent implements OnInit {
  families: any[] = [];
  featuredArticles: any[] = [];

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.loadFamilies();
    this.loadFeaturedArticles()
  }
  
  loadFamilies(): void {
    this.http.get('http://127.0.0.1:5000/articles/families')
      .subscribe((data) => {
        this.families = this.families.concat(data);
      });
  }

  loadFeaturedArticles(): void {
    this.http.get('http://127.0.0.1:5000/articles/featured')
      .subscribe((data) => {
        this.featuredArticles = this.featuredArticles.concat(data);
      });
  }

  onFamilyScroll(event: WheelEvent): void {
    const scrollContainer = event.currentTarget as HTMLElement;
    if (event.deltaY !== 0) {
      event.preventDefault();
      const scrollAmount = event.deltaY * 2;
      scrollContainer.scrollLeft += scrollAmount;
      
    }
  }



}
