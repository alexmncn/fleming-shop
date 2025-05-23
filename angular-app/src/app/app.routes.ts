import { Routes } from '@angular/router';

import { CatalogComponent } from './features/catalog/catalog.component';
import { HomeComponent } from './features/catalog/home/home.component';
import { SearchComponent } from './features/catalog/search/search.component';
import { FamilyComponent } from './features/catalog/family/family.component';
import { AuthComponent } from './features/auth/auth.component';
import { LoginComponent } from './features/auth/login/login.component';
import { RegisterComponent } from './features/auth/register/register.component';
import { authGuard } from './guards/auth.guard';
import { AdminComponent } from './features/admin/admin.component';
import { SalesComponent } from './features/admin/sales/sales.component';


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
        children: [
            { path: '', redirectTo: 'sales', pathMatch: 'full' },
            { path: 'sales', component: SalesComponent }

        ]
    },
    { path: '**', redirectTo: '/catalog' }
];
