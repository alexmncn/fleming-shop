import { Routes } from '@angular/router';

import { HomeComponent } from './features/home/home.component';
import { SearchComponent } from './features/search/search.component';
import { FamilyComponent } from './features/family/family.component';


export const routes: Routes = [
    { path: '', redirectTo: '/home', pathMatch: 'full' },
    { path: 'home', component: HomeComponent },
    { path: 'search', component: SearchComponent },
    { path: 'family', component: FamilyComponent}
];
