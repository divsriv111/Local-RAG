import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { WorkspaceListComponent } from './workspace-list/workspace-list.component';
import { WorkspaceDetailComponent } from './workspace-detail/workspace-detail.component';

const routes: Routes = [
  {
    path: '',
    component: WorkspaceListComponent,
  },
  {
    path: ':id',
    component: WorkspaceDetailComponent,
  },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
})
export class WorkspaceModule {}
