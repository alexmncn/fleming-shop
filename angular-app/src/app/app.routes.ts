import { Routes } from '@angular/router';

import { CatalogComponent } from './features/catalog/catalog.component';
import { HomeComponent } from './features/home/home.component';
import { SearchComponent } from './features/search/search.component';
import { FamilyComponent } from './features/family/family.component';
import { AuthComponent } from './features/auth/auth.component';
import { LoginComponent } from './features/auth/login/login.component';
import { RegisterComponent } from './features/auth/register/register.component';
import { authGuard } from './guards/auth.guard';
import { AdminComponent } from './features/admin/admin.component';


export const routes: Routes = [
    { path: '', redirectTo: '/catalog/home', pathMatch: 'full' },
    {
        path: 'catalog', 
        component: CatalogComponent,
        children: [
            { path: '', redirectTo: 'home', pathMatch: 'full' },
            { path: 'home', component: HomeComponent },
            { path: 'search', component: SearchComponent },
            { path: 'family', component: FamilyComponent }
        ]
    },
    { 
        path: 'auth', 
        component: AuthComponent,
        children: [
            { path: '', redirectTo: 'login', pathMatch: 'full' },
            { path: 'login', component: LoginComponent, canActivate: [authGuard] },
            { path: 'register', component: RegisterComponent, canActivate: [authGuard] }
        ]

    },
    {
        path: 'admin',
        component: AdminComponent,
        canActivate: [authGuard],
        children: []
    },
    { path: '**', redirectTo: '/catalog' }
];
